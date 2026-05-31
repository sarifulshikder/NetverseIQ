from decimal import Decimal
"""Support Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import Numeric, String, Boolean, DateTime, Text, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
import enum


class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class TicketPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


def register_models(Base):
    """Register Support models with the shared SQLAlchemy Base."""

    class Ticket(Base):
        __tablename__ = "support_tickets"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        ticket_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
        customer_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
        
        subject: Mapped[str] = mapped_column(String(256), nullable=False)
        description: Mapped[str] = mapped_column(Text, nullable=False)
        
        status: Mapped[TicketStatus] = mapped_column(
            Enum(TicketStatus), default=TicketStatus.open
        )
        priority: Mapped[TicketPriority] = mapped_column(
            Enum(TicketPriority), default=TicketPriority.medium
        )
        
        category_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # Linked to TicketCategory
        assigned_to: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # Staff/Technician ID
        
        source: Mapped[str] = mapped_column(String(64), default="web") # web, app, phone, sms, email
        
        sla_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
        is_sla_breached: Mapped[bool] = mapped_column(Boolean, default=False)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )

        replies = relationship("TicketReply", back_populates="ticket", cascade="all, delete-orphan")
        visits = relationship("FieldVisit", back_populates="ticket", cascade="all, delete-orphan")

    class TicketReply(Base):
        __tablename__ = "ticket_replies"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        ticket_id: Mapped[int] = mapped_column(ForeignKey("support_tickets.id"))
        user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # Staff ID
        customer_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        
        message: Mapped[str] = mapped_column(Text)
        is_internal: Mapped[bool] = mapped_column(Boolean, default=False)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        ticket = relationship("Ticket", back_populates="replies")

    class TicketCategory(Base):
        __tablename__ = "ticket_categories"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), unique=True)
        sla_hours: Mapped[int] = mapped_column(Integer, default=24)
        description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    class FieldVisit(Base):
        __tablename__ = "field_visits"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        ticket_id: Mapped[int] = mapped_column(ForeignKey("support_tickets.id"))
        technician_id: Mapped[int] = mapped_column(Integer)
        
        scheduled_at: Mapped[datetime] = mapped_column(DateTime)
        completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
        
        status: Mapped[str] = mapped_column(String(32), default="scheduled") # scheduled, in_progress, completed, cancelled
        notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        
        ticket = relationship("Ticket", back_populates="visits")

    return {
        "Ticket": Ticket,
        "TicketReply": TicketReply,
        "TicketCategory": TicketCategory,
        "FieldVisit": FieldVisit
    }
