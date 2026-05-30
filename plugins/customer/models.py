"""Customer Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Enum, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
import enum


class CustomerStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    expired = "expired"
    pending = "pending"


class CustomerType(str, enum.Enum):
    individual = "individual"
    corporate = "corporate"
    reseller = "reseller"


def register_models(Base):
    """Register Customer models with the shared SQLAlchemy Base."""

    class Customer(Base):
        __tablename__ = "customers"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        customer_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=True) # e.g., CUS-2024-0001
        name: Mapped[str] = mapped_column(String(256), nullable=False)
        email: Mapped[str] = mapped_column(String(256), unique=True, index=True, nullable=False)
        phone: Mapped[str] = mapped_column(String(32), default="")
        
        customer_type: Mapped[CustomerType] = mapped_column(
            Enum(CustomerType), default=CustomerType.individual
        )
        
        # New fields from roadmap
        nid_passport: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
        photo: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
        installation_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        gps_coordinates: Mapped[Optional[str]] = mapped_column(String(128), nullable=True) # "lat,lng"
        
        # Existing fields
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
        tags: Mapped[Optional[str]] = mapped_column(String(256), nullable=True) # Comma-separated labels
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )

        # Relationships
        documents = relationship("CustomerDocument", back_populates="customer", cascade="all, delete-orphan")
        contacts = relationship("CustomerContact", back_populates="customer", cascade="all, delete-orphan")
        addresses = relationship("CustomerAddress", back_populates="customer", cascade="all, delete-orphan")
        staff_notes = relationship("CustomerNote", back_populates="customer", cascade="all, delete-orphan")

    class CustomerDocument(Base):
        __tablename__ = "customer_documents"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
        doc_type: Mapped[str] = mapped_column(String(64)) # NID, Passport, Contract, etc.
        file_path: Mapped[str] = mapped_column(String(512))
        expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        customer = relationship("Customer", back_populates="documents")

    class CustomerAddress(Base):
        __tablename__ = "customer_addresses"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
        address_type: Mapped[str] = mapped_column(String(64)) # Billing, Installation
        address_text: Mapped[str] = mapped_column(Text)
        gps_coordinates: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        customer = relationship("Customer", back_populates="addresses")

    class CustomerContact(Base):
        __tablename__ = "customer_contacts"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
        name: Mapped[str] = mapped_column(String(256))
        phone: Mapped[str] = mapped_column(String(32))
        email: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        relation: Mapped[Optional[str]] = mapped_column(String(64), nullable=True) # e.g., Manager, Relative
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        customer = relationship("Customer", back_populates="contacts")

    class CustomerNote(Base):
        __tablename__ = "customer_notes"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
        author_id: Mapped[int] = mapped_column(Integer) # User ID of staff
        content: Mapped[str] = mapped_column(Text)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        customer = relationship("Customer", back_populates="staff_notes")

    return {
        "Customer": Customer,
        "CustomerDocument": CustomerDocument,
        "CustomerAddress": CustomerAddress,
        "CustomerContact": CustomerContact,
        "CustomerNote": CustomerNote
    }
