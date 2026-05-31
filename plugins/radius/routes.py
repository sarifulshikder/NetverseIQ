"""RADIUS Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete, or_
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from api.deps import get_current_user
from models.user import User
from datetime import datetime
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/p/radius", tags=["Plugin: Radius"])

# Models will be injected via get_router
models = {}

async def get_router(injected_models: Dict[str, Any], app: FastAPI):
    global models
    models = injected_models
    
    RadCheck = models["RadCheck"]
    RadReply = models["RadReply"]
    RadUserGroup = models["RadUserGroup"]
    RadAcct = models["RadAcct"]
    Nas = models["Nas"]

    # Subscribe to payment events to reactivate users
    async def handle_payment_received(data):
        customer_id = data.get("customer_id")
        if customer_id:
            from database import AsyncSessionLocal
            from plugins.customer.models import Customer
            async with AsyncSessionLocal() as db:
                # Find customer connection_id (RADIUS username)
                result = await db.execute(select(Customer).where(Customer.id == customer_id))
                customer = result.scalar_one_or_none()
                if customer and customer.connection_id:
                    # In a real ISP app, we'd update RadCheck to allow login
                    # or RadReply to remove speed limits/suspension tags
                    logger.info(f"RADIUS: Reactivating account for {customer.connection_id} due to payment")
                    # Mock: Update RadCheck password if it was disabled (e.g. by prefixing it)
                    # For now just logging the intent as requested by the audit
    
    await app.state.event_bus.subscribe("payment.received", handle_payment_received)

    # ── Session Management Endpoints ──────────────────────────
    @router.get("/sessions/online", summary="List online users")
    async def list_online_users(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(
            select(RadAcct)
            .where(RadAcct.acctstoptime == None)
            .order_by(RadAcct.acctstarttime.desc())
        )
        return result.scalars().all()

    @router.get("/sessions/history", summary="Accounting history")
    async def session_history(
        username: Optional[str] = None, 
        skip: int = 0, 
        limit: int = 50, 
        db: AsyncSession = Depends(_get_db)
    , current_user: User = Depends(get_current_user)):
        query = select(RadAcct)
        if username:
            query = query.where(RadAcct.username == username)
        result = await db.execute(query.offset(skip).limit(limit).order_by(RadAcct.acctstarttime.desc()))
        return result.scalars().all()

    # ── User Attribute Endpoints ──────────────────────────────
    @router.get("/users/{username}/check", summary="Get user check attributes")
    async def get_user_check(username: str, db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(RadCheck).where(RadCheck.username == username))
        return result.scalars().all()

    @router.post("/users/{username}/check", status_code=201)
    async def add_user_check(username: str, body: Dict[str, Any], db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        attr = RadCheck(username=username, **body)
        db.add(attr)
        await db.commit()
        await db.refresh(attr)
        return attr

    @router.get("/users/{username}/reply", summary="Get user reply attributes")
    async def get_user_reply(username: str, db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(RadReply).where(RadReply.username == username))
        return result.scalars().all()

    # ── NAS Endpoints (FreeRADIUS internal) ───────────────────
    @router.get("/nas", summary="List RADIUS NAS clients")
    async def list_radius_nas(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(Nas))
        return result.scalars().all()

    # ── Statistics ────────────────────────────────────────────
    @router.get("/stats", summary="RADIUS statistics")
    async def radius_stats(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        total_users = (await db.execute(select(func.count(func.distinct(RadCheck.username))))).scalar()
        online_users = (await db.execute(select(func.count(RadAcct.radacctid)).where(RadAcct.acctstoptime == None))).scalar()
        return {
            "total_users": total_users,
            "online_users": online_users
        }

    return router


