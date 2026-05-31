"""Subscription Plugin — SQLAlchemy Models"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
import enum


class SubscriptionStatus(str, enum.Enum):
    new = "new"
    active = "active"
    suspended = "suspended"
    expired = "expired"
    terminated = "terminated"


def register_models(Base):
    """Register Subscription models with the shared SQLAlchemy Base."""

    class Subscription(Base):
        __tablename__ = "subscriptions"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
        package_id: Mapped[int] = mapped_column(Integer, ForeignKey("isp_packages.id"), nullable=False, index=True)
        
        connection_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=True)
        
        status: Mapped[SubscriptionStatus] = mapped_column(
            Enum(SubscriptionStatus), default=SubscriptionStatus.active
        )
        
        start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
        billing_date: Mapped[Optional[int]] = mapped_column(Integer, default=1) # Day of month
        
        monthly_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
        auto_renew: Mapped[bool] = mapped_column(Boolean, default=True)
        
        # Technical
        assigned_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
        mac_address: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
        
        notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )

        history = relationship("SubscriptionHistory", back_populates="subscription", cascade="all, delete-orphan")
        addons = relationship("SubscriptionAddon", back_populates="subscription", cascade="all, delete-orphan")

    class SubscriptionHistory(Base):
        __tablename__ = "subscription_history"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"))
        action: Mapped[str] = mapped_column(String(64)) # status_change, package_change, renewal
        old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        subscription = relationship("Subscription", back_populates="history")

    class SubscriptionAddon(Base):
        __tablename__ = "subscription_addons"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"))
        addon_id: Mapped[int] = mapped_column(Integer) # Linked to package_addons.id
        price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        subscription = relationship("Subscription", back_populates="addons")

    return {
        "Subscription": Subscription,
        "SubscriptionHistory": SubscriptionHistory,
        "SubscriptionAddon": SubscriptionAddon
    }
