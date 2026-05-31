from decimal import Decimal
"""Notification Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import Numeric, String, Boolean, DateTime, Text, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


def register_models(Base):
    """Register Notification models with the shared SQLAlchemy Base."""

    class NotificationTemplate(Base):
        __tablename__ = "notification_templates"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), unique=True) # welcome_msg, invoice_reminder
        subject: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        body: Mapped[str] = mapped_column(Text)
        channel: Mapped[str] = mapped_column(String(32)) # email, sms, push
        variables: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # {customer_name: "Customer Name"}
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class Notification(Base):
        __tablename__ = "notifications"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        recipient: Mapped[str] = mapped_column(String(256), index=True)
        channel: Mapped[str] = mapped_column(String(32), default="email")
        subject: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        message: Mapped[str] = mapped_column(Text)
        
        status: Mapped[str] = mapped_column(String(32), default="pending") # pending, sent, failed
        is_read: Mapped[bool] = mapped_column(Boolean, default=False)
        
        sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class NotificationSchedule(Base):
        __tablename__ = "notification_schedules"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        template_id: Mapped[int] = mapped_column(ForeignKey("notification_templates.id"))
        recipient_filter: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # {area_id: 1}
        scheduled_at: Mapped[datetime] = mapped_column(DateTime)
        is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    return {
        "NotificationTemplate": NotificationTemplate,
        "Notification": Notification,
        "NotificationSchedule": NotificationSchedule
    }
