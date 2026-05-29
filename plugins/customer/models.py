"""Customer Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum


class CustomerStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    expired = "expired"
    pending = "pending"


def register_models(Base):
    """Register Customer model with the shared SQLAlchemy Base."""

    class Customer(Base):
        __tablename__ = "customers"

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(256), nullable=False)
        email: Mapped[str] = mapped_column(String(256), unique=True, index=True, nullable=False)
        phone: Mapped[str] = mapped_column(String(32), default="")
        address: Mapped[str] = mapped_column(Text, default="")
        area_zone: Mapped[str] = mapped_column(String(128), default="")
        connection_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, default="")
        status: Mapped[str] = mapped_column(
            Enum(CustomerStatus), default=CustomerStatus.pending
        )
        package_name: Mapped[str] = mapped_column(String(128), default="")
        monthly_fee: Mapped[float] = mapped_column(default=0.0)
        ip_address: Mapped[str] = mapped_column(String(45), default="")
        mac_address: Mapped[str] = mapped_column(String(32), default="")
        notes: Mapped[str] = mapped_column(Text, default="")
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )

    return Customer
