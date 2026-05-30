"""
NetverseIQ Plugin: Core Settings
Registers settings models and API routes.
"""
from fastapi import FastAPI
from core_settings.models import register_models
from core_settings.routes import get_router

def register(app: FastAPI, Base) -> None:
    """Called by PluginLoader — mounts routes and registers models."""
    
    # Register models and get them back
    models = register_models(Base)
    
    # Get router with models injected
    router = get_router(models)
    
    # Add prefix and tags to router if needed (manifest usually handles prefix but loader might not)
    # Looking at plugin_loader.py, it calls module.register(app, Base)
    # It doesn't seem to use api_prefix from manifest for routing automatically, 
    # it expects the plugin to mount its own routes.    
    app.include_router(router)
