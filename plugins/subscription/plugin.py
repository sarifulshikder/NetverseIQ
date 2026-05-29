"""
NetverseIQ Plugin: Customer Subscriptions
Links customers to packages and tracks billing cycles.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete, DateTime, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timedelta
from typing import Optional

def register(app, Base):
    from database import get_db

    class Subscription(Base):
        __tablename__ = "subscriptions"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
        package_id: Mapped[int] = mapped_column(Integer, ForeignKey("isp_packages.id"), nullable=False, index=True)
        status: Mapped[str] = mapped_column(String(32), default="active")
        start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
        monthly_price: Mapped[float] = mapped_column(Float, default=0.0)
        auto_renew: Mapped[bool] = mapped_column(Boolean, default=True)
        connection_details: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    router = APIRouter(prefix="/api/p/subscription", tags=["Plugin: Subscriptions"])

    def _clean(obj):
        if not obj: return None
        d = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        d.pop("sa_instance_state", None)
        return d

    @router.get("/list")
    async def list_subscriptions(skip: int = 0, limit: int = 50, status: str = "", db: AsyncSession = Depends(get_db)):
        q = select(Subscription)
        if status:
            q = q.where(Subscription.status == status)
        result = await db.execute(q.offset(skip).limit(limit).order_by(Subscription.start_date.desc()))
        total = (await db.execute(select(func.count(Subscription.id)))).scalar()
        return {"total": total, "items": [_clean(r) for r in result.scalars().all()]}

    @router.get("/{sub_id}")
    async def get_subscription(sub_id: int, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Subscription).where(Subscription.id == sub_id))
        sub = result.scalar_one_or_none()
        if not sub:
            raise HTTPException(404, "Subscription not found")
        return _clean(sub)

    @router.post("/", status_code=201)
    async def create_subscription(body: dict, db: AsyncSession = Depends(get_db)):
        body.pop("id", None)
        body.pop("created_at", None)
        body.pop("updated_at", None)
        sub = Subscription(**body)
        db.add(sub)
        await db.commit()
        await db.refresh(sub)
        return _clean(sub)

    @router.put("/{sub_id}")
    async def update_subscription(sub_id: int, body: dict, db: AsyncSession = Depends(get_db)):
        body.pop("id", None)
        await db.execute(update(Subscription).where(Subscription.id == sub_id).values(**body))
        await db.commit()
        result = await db.execute(select(Subscription).where(Subscription.id == sub_id))
        return _clean(result.scalar_one_or_none())

    @router.delete("/{sub_id}", status_code=204)
    async def delete_subscription(sub_id: int, db: AsyncSession = Depends(get_db)):
        await db.execute(delete(Subscription).where(Subscription.id == sub_id))
        await db.commit()

    @router.get("/customer/{customer_id}")
    async def get_by_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Subscription).where(Subscription.customer_id == customer_id))
        return [_clean(r) for r in result.scalars().all()]

    @router.get("/expiring-soon")
    async def expiring_soon(days: int = 7, db: AsyncSession = Depends(get_db)):
        threshold = datetime.utcnow() + timedelta(days=days)
        result = await db.execute(
            select(Subscription)
            .where(Subscription.end_date <= threshold)
            .where(Subscription.status == "active")
        )
        return [_clean(r) for r in result.scalars().all()]

    @router.post("/{sub_id}/renew")
    async def renew_subscription(sub_id: int, months: int = 1, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Subscription).where(Subscription.id == sub_id))
        sub = result.scalar_one_or_none()
        if not sub:
            raise HTTPException(404, "Subscription not found")
        new_end = (sub.end_date or sub.start_date) + timedelta(days=30 * months)
        await db.execute(
            update(Subscription)
            .where(Subscription.id == sub_id)
            .values(end_date=new_end, status="active", updated_at=datetime.utcnow())
        )
        await db.commit()
        await db.refresh(sub)
        return _clean(sub)

    @router.post("/{sub_id}/suspend")
    async def suspend_subscription(sub_id: int, db: AsyncSession = Depends(get_db)):
        await db.execute(
            update(Subscription)
            .where(Subscription.id == sub_id)
            .values(status="suspended", updated_at=datetime.utcnow())
        )
        await db.commit()
        result = await db.execute(select(Subscription).where(Subscription.id == sub_id))
        return _clean(result.scalar_one_or_none())

    app.include_router(router)
