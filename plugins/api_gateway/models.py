from decimal import Decimal
"""API Gateway Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import Numeric, String, Boolean, DateTime, Text, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


def register_models(Base):
    """Register API Gateway models with the shared SQLAlchemy Base."""

    class APIKey(Base):
        __tablename__ = "api_keys"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128))
        api_key: Mapped[str] = mapped_column(String(256), unique=True, index=True)
        
        rate_limit: Mapped[int] = mapped_column(Integer, default=1000) # Requests per day
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    class Webhook(Base):
        __tablename__ = "webhooks"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        url: Mapped[str] = mapped_column(String(512))
        event_type: Mapped[str] = mapped_column(String(64)) # payment.received, customer.created
        secret: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    return {
        "APIKey": APIKey,
        "Webhook": Webhook
    }
