"""Multi-Tenant Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, JSON, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


def register_models(Base):
    """Register Multi-Tenant models with the shared SQLAlchemy Base."""

    class TenantPlan(Base):
        __tablename__ = "tenant_plans"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(64), unique=True) # Basic, Pro, Enterprise
        
        max_customers: Mapped[int] = mapped_column(Integer, default=100)
        max_nas: Mapped[int] = mapped_column(Integer, default=1)
        monthly_price: Mapped[float] = mapped_column(Float, default=0.0)
        
        features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # {"radius": True, "hrm": False}

    class Tenant(Base):
        __tablename__ = "tenants"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        company_name: Mapped[str] = mapped_column(String(256), index=True)
        subdomain: Mapped[str] = mapped_column(String(128), unique=True, index=True)
        
        plan_id: Mapped[int] = mapped_column(ForeignKey("tenant_plans.id"))
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        
        admin_email: Mapped[str] = mapped_column(String(256))
        db_schema: Mapped[Optional[str]] = mapped_column(String(128), nullable=True) # For schema isolation
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    return {
        "TenantPlan": TenantPlan,
        "Tenant": Tenant
    }
