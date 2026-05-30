"""Subscription Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/p/subscription", tags=["Plugin: Subscription"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    Subscription = models["Subscription"]
    SubscriptionHistory = models["SubscriptionHistory"]
    SubscriptionAddon = models["SubscriptionAddon"]

    # ── Subscription Endpoints ────────────────────────────────
    @router.get("/", summary="List all subscriptions")
    async def list_subscriptions(
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        db: AsyncSession = Depends(_get_db),
    ):
        query = select(Subscription)
        if status:
            query = query.where(Subscription.status == status)
        result = await db.execute(query.offset(skip).limit(limit).order_by(Subscription.created_at.desc()))
        items = result.scalars().all()
        total = (await db.execute(select(func.count(Subscription.id)))).scalar()
        return {"total": total, "items": items}

    @router.post("/", status_code=status.HTTP_201_CREATED, summary="Create subscription")
    async def create_subscription(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        from .models import SubscriptionStatus
        if "status" in body and isinstance(body["status"], str):
            body["status"] = SubscriptionStatus(body["status"])
            
        sub = Subscription(**body)
        db.add(sub)
        await db.commit()
        await db.refresh(sub)
        
        # Log history
        history = SubscriptionHistory(
            subscription_id=sub.id,
            action="create",
            new_value=f"Package ID: {sub.package_id}, Status: {sub.status}"
        )
        db.add(history)
        await db.commit()
        
        return sub

    @router.get("/stats", summary="Subscription statistics")
    async def subscription_stats(db: AsyncSession = Depends(_get_db)):
        total = (await db.execute(select(func.count(Subscription.id)))).scalar()
        active = (await db.execute(select(func.count(Subscription.id)).where(Subscription.status == "active"))).scalar()
        suspended = (await db.execute(select(func.count(Subscription.id)).where(Subscription.status == "suspended"))).scalar()
        expired = (await db.execute(select(func.count(Subscription.id)).where(Subscription.status == "expired"))).scalar()
        
        # Expiring soon (next 7 days)
        threshold = datetime.utcnow() + timedelta(days=7)
        expiring_soon = (await db.execute(
            select(func.count(Subscription.id))
            .where(Subscription.end_date <= threshold)
            .where(Subscription.status == "active")
        )).scalar()
        
        return {
            "total": total,
            "active": active,
            "suspended": suspended,
            "expired": expired,
            "expiring_soon": expiring_soon
        }

    @router.get("/{sub_id}", summary="Get subscription by ID")
    async def get_subscription(sub_id: int, db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Subscription).where(Subscription.id == sub_id))
        sub = result.scalar_one_or_none()
        if not sub:
            raise HTTPException(404, "Subscription not found")
        return sub

    @router.get("/{sub_id}/history", summary="Subscription history")
    async def get_subscription_history(sub_id: int, db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(SubscriptionHistory).where(SubscriptionHistory.subscription_id == sub_id).order_by(SubscriptionHistory.created_at.desc()))
        return result.scalars().all()

    @router.post("/{sub_id}/upgrade", summary="Upgrade/Change package")
    async def upgrade_subscription(sub_id: int, body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Subscription).where(Subscription.id == sub_id))
        sub = result.scalar_one_or_none()
        if not sub:
            raise HTTPException(404, "Subscription not found")
            
        old_package_id = sub.package_id
        new_package_id = body.get("package_id")
        
        if not new_package_id:
            raise HTTPException(400, "New package_id is required")
            
        sub.package_id = new_package_id
        if "monthly_price" in body:
            sub.monthly_price = body["monthly_price"]
            
        history = SubscriptionHistory(
            subscription_id=sub.id,
            action="package_change",
            old_value=f"Package ID: {old_package_id}",
            new_value=f"Package ID: {new_package_id}",
            reason=body.get("reason", "")
        )
        db.add(history)
        await db.commit()
        await db.refresh(sub)
        return sub

    @router.put("/{sub_id}", summary="Update subscription")
    async def update_subscription(sub_id: int, body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Subscription).where(Subscription.id == sub_id))
        sub = result.scalar_one_or_none()
        if not sub:
            raise HTTPException(404, "Subscription not found")
            
        for k, v in body.items():
            if hasattr(sub, k) and k not in ("id", "created_at"):
                if k == "status" and isinstance(v, str):
                    from .models import SubscriptionStatus
                    v = SubscriptionStatus(v)
                setattr(sub, k, v)
        
        await db.commit()
        await db.refresh(sub)
        return sub

    return router


def _get_db():
    from database import get_db
    return Depends(get_db)
