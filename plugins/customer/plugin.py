"""
NetverseIQ Plugin: Customer Management
Registers Customer model and API routes with the core application.
"""
from fastapi import FastAPI
from customer.models import register_models
from customer.routes import get_router

def register(app: FastAPI, Base) -> None:
    """Called by PluginLoader — mounts routes and registers models."""
    
    # Register models and get them back
    models = register_models(Base)
    
    # Get router with models injected
    router = get_router(models)    
    app.include_router(router)
