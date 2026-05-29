"""
NetverseIQ Plugin: Customer Management
Registers Customer model and API routes with the core application.
"""
import sys
import os

# Ensure plugin dir is importable
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import APIRouter, Depends, HTTPException, status as http_status


def register(app: FastAPI, Base) -> None:
    """Called by PluginLoader — mounts routes and registers models."""

    # ── Register Model ────────────────────────────────────────
    from datetime import datetime
    from sqlalchemy import String, Text, Integer, Enum as SAEnum, Float
    from sqlalchemy.orm import Mapped, mapped_column
    import enum

    class CustomerStatus(str, enum.Enum):
        active = "active"
        suspended = "suspended"
        expired = "expired"
        pending = "pending"

    class Customer(Base):
        __tablename__ = "customers"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(256), nullable=False)
        email: Mapped[str] = mapped_column(String(256), unique=True, index=True, nullable=False)
        phone: Mapped[str] = mapped_column(String(32), default="")
        address: Mapped[str] = mapped_column(Text, default="")
        area_zone: Mapped[str] = mapped_column(String(128), default="")
        connection_id: Mapped[str] = mapped_column(String(64), default="")
        status: Mapped[str] = mapped_column(String(32), default="pending")
        package_name: Mapped[str] = mapped_column(String(128), default="")
        monthly_fee: Mapped[float] = mapped_column(Float, default=0.0)
        ip_address: Mapped[str] = mapped_column(String(45), default="")
        mac_address: Mapped[str] = mapped_column(String(32), default="")
        notes: Mapped[str] = mapped_column(Text, default="")
        created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(
            default=datetime.utcnow, onupdate=datetime.utcnow
        )

    # ── Build Router ──────────────────────────────────────────
    from database import get_db

    router = APIRouter(prefix="/api/p/customer", tags=["Plugin: Customers"])

    @router.get("/", summary="List customers")
    async def list_customers(
        skip: int = 0, limit: int = 50, search: str = "",
        db: AsyncSession = Depends(get_db),
    ):
        query = select(Customer)
        if search:
            query = query.where(
                Customer.name.ilike(f"%{search}%")
                | Customer.email.ilike(f"%{search}%")
                | Customer.connection_id.ilike(f"%{search}%")
            )
        result = await db.execute(query.offset(skip).limit(limit))
        items = [row.__dict__ for row in result.scalars().all()]
        for i in items:
            i.pop("_sa_instance_state", None)
        count = (await db.execute(select(func.count(Customer.id)))).scalar()
        return {"total": count, "items": items}

    @router.get("/stats", summary="Customer statistics")
    async def stats(db: AsyncSession = Depends(get_db)):
        total    = (await db.execute(select(func.count(Customer.id)))).scalar()
        active   = (await db.execute(select(func.count(Customer.id)).where(Customer.status == "active"))).scalar()
        suspended= (await db.execute(select(func.count(Customer.id)).where(Customer.status == "suspended"))).scalar()
        pending  = (await db.execute(select(func.count(Customer.id)).where(Customer.status == "pending"))).scalar()
        return {"total": total, "active": active, "suspended": suspended, "pending": pending,
                "expired": max(0, total - active - suspended - pending)}

    @router.post("/", status_code=201, summary="Create customer")
    async def create_customer(body: dict, db: AsyncSession = Depends(get_db)):
        body.pop("id", None)
        body.pop("created_at", None)
        body.pop("updated_at", None)
        c = Customer(**body)
        db.add(c)
        await db.commit()
        await db.refresh(c)
        d = c.__dict__.copy()
        d.pop("_sa_instance_state", None)
        return d

    @router.get("/{customer_id}", summary="Get customer")
    async def get_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
        r = await db.execute(select(Customer).where(Customer.id == customer_id))
        c = r.scalar_one_or_none()
        if not c:
            raise HTTPException(404, "Customer not found")
        d = c.__dict__.copy(); d.pop("_sa_instance_state", None)
        return d

    @router.put("/{customer_id}", summary="Update customer")
    async def update_customer(customer_id: int, body: dict, db: AsyncSession = Depends(get_db)):
        r = await db.execute(select(Customer).where(Customer.id == customer_id))
        c = r.scalar_one_or_none()
        if not c:
            raise HTTPException(404, "Customer not found")
        for k, v in body.items():
            if hasattr(c, k) and k not in ("id", "created_at"):
                setattr(c, k, v)
        await db.commit()
        await db.refresh(c)
        d = c.__dict__.copy(); d.pop("_sa_instance_state", None)
        return d

    @router.delete("/{customer_id}", status_code=204, summary="Delete customer")
    async def delete_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
        r = await db.execute(select(Customer).where(Customer.id == customer_id))
        c = r.scalar_one_or_none()
        if not c:
            raise HTTPException(404, "Customer not found")
        await db.delete(c)
        await db.commit()

    app.include_router(router)
