"""
NetverseIQ Plugin: Expense & Accounts
Registers Expense models and API routes.
"""
from fastapi import FastAPI
from expense.models import register_models
from expense.routes import get_router

def register(app: FastAPI, Base) -> None:
    """Called by PluginLoader — mounts routes and registers models."""
    
    # Register models and get them back
    models = register_models(Base)
    
    # Get router with models injected
    router = get_router(models)    
    app.include_router(router)
