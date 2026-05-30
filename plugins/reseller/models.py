"""Reseller Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


def register_models(Base):
    """Register Reseller models with the shared SQLAlchemy Base."""

    class Reseller(Base):
        __tablename__ = "resellers"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(256), index=True)
        company_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        
        email: Mapped[str] = mapped_column(String(256), unique=True, index=True)
        phone: Mapped[str] = mapped_column(String(32))
        
        commission_type: Mapped[str] = mapped_column(String(32), default="percentage") # percentage, fixed
        commission_value: Mapped[float] = mapped_column(Float, default=10.0)
        
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        wallet = relationship("ResellerWallet", back_populates="reseller", uselist=False)

    class ResellerCustomer(Base):
        __tablename__ = "reseller_customers"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        reseller_id: Mapped[int] = mapped_column(ForeignKey("resellers.id"))
        customer_id: Mapped[int] = mapped_column(Integer, unique=True) # Linked to customers.id

    class ResellerWallet(Base):
        __tablename__ = "reseller_wallets"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        reseller_id: Mapped[int] = mapped_column(ForeignKey("resellers.id"))
        balance: Mapped[float] = mapped_column(Float, default=0.0)
        
        reseller = relationship("Reseller", back_populates="wallet")

    class ResellerPackagePrice(Base):
        __tablename__ = "reseller_package_prices"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        reseller_id: Mapped[int] = mapped_column(ForeignKey("resellers.id"))
        package_id: Mapped[int] = mapped_column(Integer) # Linked to isp_packages.id
        custom_price: Mapped[float] = mapped_column(Float)

    return {
        "Reseller": Reseller,
        "ResellerCustomer": ResellerCustomer,
        "ResellerWallet": ResellerWallet,
        "ResellerPackagePrice": ResellerPackagePrice
    }
