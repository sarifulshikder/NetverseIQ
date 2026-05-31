"""
NetverseIQ Plugin: RADIUS Management
Registers FreeRADIUS-compatible models and API routes.
"""
from fastapi import FastAPI
from radius.models import register_models
from radius.routes import get_router

async def register(app: FastAPI, Base) -> None:
    """Called by PluginLoader — mounts routes and registers models."""
    
    # Register models and get them back
    models = register_models(Base)
    
    # Get router with models injected
    router = await get_router(models, app)    
    app.include_router(router)
