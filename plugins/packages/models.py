from decimal import Decimal
"""Packages Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import Numeric, String, Boolean, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


def register_models(Base):
    """Register Packages models with the shared SQLAlchemy Base."""

    class PackageCategory(Base):
        __tablename__ = "package_categories"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
        description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        
        packages = relationship("Package", back_populates="category")

    class Package(Base):
        __tablename__ = "isp_packages"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
        category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("package_categories.id"), nullable=True)
        
        speed_mbps: Mapped[int] = mapped_column(Integer, nullable=False)
        upload_speed_mbps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        
        # Pricing
        price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
        installation_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
        security_deposit: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
        vat_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=15.0)
        
        validity_days: Mapped[int] = mapped_column(Integer, default=30)
        
        description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        
        # RADIUS Integration
        radius_profile: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
        
        # Reseller
        reseller_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )

        category = relationship("PackageCategory", back_populates="packages")
        promotions = relationship("PackagePromotion", back_populates="package")

    class PackagePromotion(Base):
        __tablename__ = "package_promotions"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        package_id: Mapped[int] = mapped_column(ForeignKey("isp_packages.id"))
        name: Mapped[str] = mapped_column(String(128))
        promo_code: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True)
        discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
        discount_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
        start_date: Mapped[datetime] = mapped_column(DateTime)
        end_date: Mapped[datetime] = mapped_column(DateTime)
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        
        package = relationship("Package", back_populates="promotions")

    class PackageAddon(Base):
        __tablename__ = "package_addons"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128))
        price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
        description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    return {
        "Package": Package,
        "PackageCategory": PackageCategory,
        "PackagePromotion": PackagePromotion,
        "PackageAddon": PackageAddon
    }
