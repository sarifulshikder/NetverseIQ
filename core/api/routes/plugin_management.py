from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import AsyncSessionLocal
from models.plugin_registry import PluginRegistry
from schemas.plugin_registry import PluginRegistrySchema, PluginRegistryUpdateSchema

router = APIRouter(prefix="/plugins", tags=["Plugins"])

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

@router.get("/", response_model=list[PluginRegistrySchema])
async def list_plugins(db: AsyncSession = Depends(get_db)):
    """List all registered plugins."""
    result = await db.execute(select(PluginRegistry))
    plugins = result.scalars().all()
    return plugins

@router.get("/{plugin_id}", response_model=PluginRegistrySchema)
async def get_plugin_details(plugin_id: str, db: AsyncSession = Depends(get_db)):
    """Get details of a specific plugin."""
    result = await db.execute(select(PluginRegistry).where(PluginRegistry.plugin_id == plugin_id))
    plugin = result.scalar_one_or_none()
    if plugin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plugin not found")
    return plugin

@router.patch("/{plugin_id}", response_model=PluginRegistrySchema)
async def update_plugin_status(
    plugin_id: str,
    plugin_update: PluginRegistryUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a plugin."""
    result = await db.execute(select(PluginRegistry).where(PluginRegistry.plugin_id == plugin_id))
    plugin = result.scalar_one_or_none()

    if plugin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plugin not found")

    plugin.is_enabled = plugin_update.is_enabled
    db.add(plugin)
    await db.commit()
    await db.refresh(plugin)
    return plugin
