"""Payment Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


def register_models(Base):
    """Register Payment models with the shared SQLAlchemy Base."""

    class Payment(Base):
        __tablename__ = "payments"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        customer_id: Mapped[int] = mapped_column(Integer, index=True)
        invoice_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        
        amount: Mapped[float] = mapped_column(Float)
        method: Mapped[str] = mapped_column(String(64)) # Cash, bKash, Card, etc.
        transaction_id: Mapped[Optional[str]] = mapped_column(String(128), unique=True, index=True)
        
        status: Mapped[str] = mapped_column(String(32), default="completed")
        reference: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class AdvancePayment(Base):
        __tablename__ = "advance_payments"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        customer_id: Mapped[int] = mapped_column(Integer, index=True)
        amount: Mapped[float] = mapped_column(Float)
        balance: Mapped[float] = mapped_column(Float)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class Refund(Base):
        __tablename__ = "refunds"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id"))
        amount: Mapped[float] = mapped_column(Float)
        reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        status: Mapped[str] = mapped_column(String(32), default="pending")
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    return {
        "Payment": Payment,
        "AdvancePayment": AdvancePayment,
        "Refund": Refund
    }
