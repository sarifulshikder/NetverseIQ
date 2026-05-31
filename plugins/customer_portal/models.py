from decimal import Decimal
"""Customer Portal Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import Numeric, String, Boolean, DateTime, Text, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


def register_models(Base):
    """Register Customer Portal models with the shared SQLAlchemy Base."""

    class PortalSession(Base):
        __tablename__ = "portal_sessions"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        customer_id: Mapped[int] = mapped_column(Integer, index=True)
        token: Mapped[str] = mapped_column(String(256), unique=True, index=True)
        expires_at: Mapped[datetime] = mapped_column(DateTime)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    return {
        "PortalSession": PortalSession
    }
