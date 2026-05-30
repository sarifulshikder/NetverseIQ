"""
NetverseIQ Plugin Loader
========================
Discovers plugins in PLUGINS_DIR, reads manifest.json,
imports plugin.py, calls register(app, Base), and syncs
state to the plugin_registry table.

Plugin contract
---------------
Each plugin directory must contain:
  manifest.json   — metadata + menu items
  plugin.py       — must expose: register(app, Base)
"""
import json
import importlib.util
import sys
import os
import logging
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import AsyncSessionLocal, Base
from models.plugin_registry import PluginRegistry

logger = logging.getLogger(__name__)


class PluginLoader:
    """Discovers and loads plugins from the filesystem."""

    def __init__(self):
        self.plugins_dir = Path(settings.PLUGINS_DIR)
        self.loaded: list[str] = []

    async def discover_and_load(self, app: FastAPI) -> None:
        """Scan plugin directory, load each plugin, sync DB registry."""
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return

        async with AsyncSessionLocal() as db:
            for plugin_dir in sorted(self.plugins_dir.iterdir()):
                if not plugin_dir.is_dir():
                    continue

                manifest_path = plugin_dir / "manifest.json"
                plugin_path = plugin_dir / "plugin.py"

                if not manifest_path.exists():
                    logger.debug(f"Skipping {plugin_dir.name}: no manifest.json")
                    continue

                try:
                    manifest = json.loads(manifest_path.read_text())
                    plugin_id = manifest.get("id", plugin_dir.name)

                    # Sync to DB registry
                    # Sync to DB registry and get the current enabled status
                    is_enabled = await self._sync_registry(db, plugin_id, manifest)

                    # Only load Python module if plugin.py exists AND the plugin is enabled
                    if plugin_path.exists():
                        if is_enabled:
                            await self._load_module(app, plugin_id, plugin_path, manifest)
                        else:
                            logger.info(f"Plugin skipped (disabled): {plugin_id}")

                    if is_enabled:
                        self.loaded.append(plugin_id)
                        logger.info(f"✓ Plugin loaded: {plugin_id} v{manifest.get('version', '?')}")
                    else:
                        logger.info(f"Plugin {plugin_id} v{manifest.get('version', '?')} registered but not loaded (disabled).")

                    self.loaded.append(plugin_id)
                    logger.info(f"✓ Plugin loaded: {plugin_id} v{manifest.get('version', '?')}")

                except Exception as exc:
                    logger.error(f"✗ Failed to load plugin '{plugin_dir.name}': {exc}", exc_info=True)

            await db.commit()

        logger.info(f"Plugin loader complete. Loaded: {self.loaded}")

    async def _sync_registry(self, db: AsyncSession, plugin_id: str, manifest: dict) -> None:
        """Upsert plugin record in plugin_registry table."""
        result = await db.execute(
            select(PluginRegistry).where(PluginRegistry.plugin_id == plugin_id)
        )
        record = result.scalar_one_or_none()

        if record is None:
            record = PluginRegistry(
                plugin_id=plugin_id,
                name=manifest.get("name", plugin_id),
                version=manifest.get("version", "1.0.0"),
                description=manifest.get("description", ""),
                author=manifest.get("author", ""),
                is_enabled=manifest.get("enabled", True),
                manifest=manifest,
            )
            db.add(record)
        else:
            # Update metadata but preserve user's enabled/disabled choice
            record.name = manifest.get("name", plugin_id)
            record.version = manifest.get("version", "1.0.0")
            record.description = manifest.get("description", "")
            record.author = manifest.get("author", "")
            record.manifest = manifest

        return record.is_enabled

    async def _load_module(
        self, app: FastAPI, plugin_id: str, plugin_path: Path, manifest: dict
    ) -> None:
        """Dynamically import plugin.py and call register(app, Base)."""
        module_name = f"plugins.{plugin_id}"

        # Add plugin parent dir to sys.path so relative imports work
        plugins_parent = str(plugin_path.parent.parent)
        if plugins_parent not in sys.path:
            sys.path.insert(0, plugins_parent)

        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot create module spec for {plugin_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        if hasattr(module, "register"):
            module.register(app, Base)
        else:
            logger.warning(f"Plugin '{plugin_id}' has no register() function — routes not mounted")
