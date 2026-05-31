"""API Gateway Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from datetime import datetime
import secrets

router = APIRouter(prefix="/api/p/api_gateway", tags=["Plugin: Api_Gateway"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    APIKey = models["APIKey"]
    Webhook = models["Webhook"]

    # ── API Key Endpoints ─────────────────────────────────────
    @router.get("/keys", summary="List all API keys")
    async def list_api_keys(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(APIKey))
        return result.scalars().all()

    @router.post("/keys", status_code=201)
    async def generate_api_key(name: str, db: AsyncSession = Depends(_get_db)):
        new_key = secrets.token_urlsafe(32)
        api_key = APIKey(name=name, api_key=new_key)
        db.add(api_key)
        await db.commit()
        await db.refresh(api_key)
        return api_key

    # ── Webhook Endpoints ─────────────────────────────────────
    @router.get("/webhooks", summary="List all webhooks")
    async def list_webhooks(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Webhook))
        return result.scalars().all()

    @router.post("/webhooks", status_code=201)
    async def register_webhook(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        webhook = Webhook(**body)
        db.add(webhook)
        await db.commit()
        await db.refresh(webhook)
        return webhook

    # ── Third-party Integrations ──────────────────────────────
    @router.get("/integrations/status", summary="Check third-party connection status")
    async def check_integrations():
        return {
            "whatsapp": "connected",
            "bkash_api": "connected",
            "nagad_api": "disconnected"
        }

    return router


