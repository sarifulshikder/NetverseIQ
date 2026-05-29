"""
NetverseIQ Plugin: Notifications & Alerts
Logs and manages notification history. Extensible for SMS/Email gateways.
"""
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime


def register(app: FastAPI, Base) -> None:

    from sqlalchemy import Integer, String, Text, DateTime, Boolean
    from sqlalchemy.orm import Mapped, mapped_column

    class Notification(Base):
        __tablename__ = "notifications"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        recipient: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
        channel: Mapped[str] = mapped_column(String(32), default="email")  # email/sms/push
        subject: Mapped[str] = mapped_column(String(256), default="")
        message: Mapped[str] = mapped_column(Text, nullable=False)
        status: Mapped[str] = mapped_column(String(32), default="pending")  # pending/sent/failed
        is_read: Mapped[bool] = mapped_column(Boolean, default=False)
        sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    from database import get_db

    router = APIRouter(prefix="/api/p/notification", tags=["Plugin: Notifications"])

    def _clean(obj):
        d = obj.__dict__.copy()
        d.pop("_sa_instance_state", None)
        return d

    @router.get("/", summary="List notifications")
    async def list_notifications(
        skip: int = 0, limit: int = 50, channel: str = "",
        db: AsyncSession = Depends(get_db),
    ):
        q = select(Notification).order_by(Notification.created_at.desc())
        if channel:
            q = q.where(Notification.channel == channel)
        result = await db.execute(q.offset(skip).limit(limit))
        total = (await db.execute(select(func.count(Notification.id)))).scalar()
        return {"total": total, "items": [_clean(r) for r in result.scalars().all()]}

    @router.post("/send", status_code=201, summary="Send / queue notification")
    async def send_notification(body: dict, db: AsyncSession = Depends(get_db)):
        """Queue a notification. Gateway integration can be added via webhook/config."""
        body.pop("id", None)
        notif = Notification(**body)
        # Mark as sent immediately (replace with actual gateway call)
        notif.status = "sent"
        notif.sent_at = datetime.utcnow()
        db.add(notif)
        await db.commit()
        await db.refresh(notif)
        return _clean(notif)

    @router.get("/unread-count", summary="Count unread notifications")
    async def unread_count(db: AsyncSession = Depends(get_db)):
        count = (await db.execute(
            select(func.count(Notification.id)).where(Notification.is_read == False)
        )).scalar()
        return {"unread": count}

    @router.patch("/{notif_id}/read", summary="Mark as read")
    async def mark_read(notif_id: int, db: AsyncSession = Depends(get_db)):
        r = await db.execute(select(Notification).where(Notification.id == notif_id))
        notif = r.scalar_one_or_none()
        if not notif:
            raise HTTPException(404, "Notification not found")
        notif.is_read = True
        await db.commit()
        return {"ok": True}

    app.include_router(router)
