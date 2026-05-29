"""
NetverseIQ — Plugin Management API Routes
GET    /api/plugins            → list all plugins
GET    /api/plugins/{id}       → get plugin detail
PATCH  /api/plugins/{id}       → enable/disable
GET    /api/plugins/menu       → sidebar menu items for enabled plugins
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Any

from database import get_db
from api.deps import get_current_user, require_superuser
from models.user import User
from models.plugin_registry import PluginRegistry
from schemas.plugin import PluginOut, PluginToggle

router = APIRouter()


@router.get("/", response_model=List[PluginOut])
async def list_plugins(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Return all discovered plugins with their status."""
    result = await db.execute(select(PluginRegistry))
    return result.scalars().all()


@router.get("/menu")
async def get_menu(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> List[Any]:
    """Return sidebar menu items from all enabled plugins."""
    result = await db.execute(
        select(PluginRegistry).where(PluginRegistry.is_enabled == True)
    )
    plugins = result.scalars().all()
    menu = []
    for p in plugins:
        items = p.manifest.get("menu", [])
        menu.extend(items)
    return menu


@router.get("/{plugin_id}", response_model=PluginOut)
async def get_plugin(
    plugin_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PluginRegistry).where(PluginRegistry.plugin_id == plugin_id)
    )
    plugin = result.scalar_one_or_none()
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin


@router.patch("/{plugin_id}", response_model=PluginOut)
async def toggle_plugin(
    plugin_id: str,
    body: PluginToggle,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_superuser),
):
    """Enable or disable a plugin (requires superuser)."""
    result = await db.execute(
        select(PluginRegistry).where(PluginRegistry.plugin_id == plugin_id)
    )
    plugin = result.scalar_one_or_none()
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    plugin.is_enabled = body.is_enabled
    await db.commit()
    await db.refresh(plugin)
    return plugin
