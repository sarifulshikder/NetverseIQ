"""Billing Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
import enum


class InvoiceStatus(str, enum.Enum):
    unpaid = "unpaid"
    paid = "paid"
    partial = "partial"
    cancelled = "cancelled"
    overdue = "overdue"


def register_models(Base):
    """Register Billing models with the shared SQLAlchemy Base."""

    class Invoice(Base):
        __tablename__ = "invoices"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        invoice_number: Mapped[str] = mapped_column(String(64), unique=True, index=True)
        customer_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
        
        status: Mapped[InvoiceStatus] = mapped_column(
            Enum(InvoiceStatus), default=InvoiceStatus.unpaid
        )
        
        sub_total: Mapped[float] = mapped_column(Float, default=0.0)
        discount: Mapped[float] = mapped_column(Float, default=0.0)
        tax_amount: Mapped[float] = mapped_column(Float, default=0.0)
        total: Mapped[float] = mapped_column(Float, default=0.0)
        
        due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
        paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
        payment_method: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
        
        notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )

        items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

    class InvoiceItem(Base):
        __tablename__ = "invoice_items"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
        description: Mapped[str] = mapped_column(String(256))
        quantity: Mapped[int] = mapped_column(Integer, default=1)
        unit_price: Mapped[float] = mapped_column(Float)
        total: Mapped[float] = mapped_column(Float)
        
        invoice = relationship("Invoice", back_populates="items")

    class CreditNote(Base):
        __tablename__ = "credit_notes"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
        amount: Mapped[float] = mapped_column(Float)
        reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class ProformaInvoice(Base):
        __tablename__ = "proforma_invoices"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        customer_id: Mapped[int] = mapped_column(Integer)
        total: Mapped[float] = mapped_column(Float)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    return {
        "Invoice": Invoice,
        "InvoiceItem": InvoiceItem,
        "CreditNote": CreditNote,
        "ProformaInvoice": ProformaInvoice
    }
