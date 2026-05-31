"""Notification Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from api.deps import get_current_user
from models.user import User
from datetime import datetime

from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/p/notification", tags=["Plugin: Notification"])

# Models will be injected via get_router
models = {}

async def get_router(injected_models: Dict[str, Any], app: FastAPI):
    global models
    models = injected_models
    
    Notification = models["Notification"]
    NotificationTemplate = models["NotificationTemplate"]
    NotificationSchedule = models["NotificationSchedule"]

    # Subscribe to events to send notifications
    async def handle_customer_created(data):
        logger.info(f"NOTIFICATION: Sending welcome message to {data.get('email')}")
        from database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            notif = Notification(
                title="Welcome to NetverseIQ",
                content=f"Welcome {data.get('name')}! Your account has been created.",
                channel="email",
                status="sent",
                sent_at=datetime.utcnow()
            )
            db.add(notif)
            await db.commit()

    async def handle_payment_received(data):
        logger.info(f"NOTIFICATION: Sending payment confirmation for amount {data.get('amount')}")
        from database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            notif = Notification(
                title="Payment Received",
                content=f"Thank you! We received your payment of {data.get('amount')}.",
                channel="sms",
                status="sent",
                sent_at=datetime.utcnow()
            )
            db.add(notif)
            await db.commit()
    
    await app.state.event_bus.subscribe("customer.created", handle_customer_created)
    await app.state.event_bus.subscribe("payment.received", handle_payment_received)

    # ── Notification Endpoints ────────────────────────────────
    @router.get("/", summary="List all notifications")
    async def list_notifications(
        skip: int = 0,
        limit: int = 50,
        channel: Optional[str] = None,
        db: AsyncSession = Depends(_get_db),
     current_user: User = Depends(get_current_user),):
        query = select(Notification)
        if channel:
            query = query.where(Notification.channel == channel)
        result = await db.execute(query.offset(skip).limit(limit).order_by(Notification.created_at.desc()))
        items = result.scalars().all()
        total = (await db.execute(select(func.count(Notification.id)))).scalar()
        return {"total": total, "items": items}

    @router.post("/send", status_code=status.HTTP_201_CREATED, summary="Send notification")
    async def send_notification(body: Dict[str, Any], db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        notification = Notification(**body)
        notification.status = "sent" # Mocking immediate delivery
        notification.sent_at = datetime.utcnow()
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification

    @router.get("/unread-count", summary="Count unread")
    async def unread_count(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        count = (await db.execute(select(func.count(Notification.id)).where(Notification.is_read == False))).scalar()
        return {"unread": count}

    # ── Template Endpoints ────────────────────────────────────
    @router.get("/templates", summary="List templates")
    async def list_templates(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(NotificationTemplate))
        return result.scalars().all()

    @router.post("/templates", status_code=201)
    async def create_template(body: Dict[str, Any], db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        template = NotificationTemplate(**body)
        db.add(template)
        await db.commit()
        await db.refresh(template)
        return template

    # ── Schedule Endpoints ────────────────────────────────────
    @router.post("/schedule", status_code=201)
    async def schedule_notification(body: Dict[str, Any], db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        schedule = NotificationSchedule(**body)
        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)
        return schedule

    return router


