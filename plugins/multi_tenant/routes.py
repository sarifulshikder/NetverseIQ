"""Multi-Tenant Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from datetime import datetime

router = APIRouter(prefix="/api/p/multi_tenant", tags=["Plugin: Multi_Tenant"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    Tenant = models["Tenant"]
    TenantPlan = models["TenantPlan"]

    # ── Tenant Endpoints ──────────────────────────────────────
    @router.get("/tenants", summary="List all tenants")
    async def list_tenants(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Tenant))
        return result.scalars().all()

    @router.post("/tenants", status_code=201)
    async def create_tenant(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        tenant = Tenant(**body)
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
        return tenant

    # ── Plan Endpoints ────────────────────────────────────────
    @router.get("/plans", summary="List tenant plans")
    async def list_plans(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(TenantPlan))
        return result.scalars().all()

    @router.post("/plans", status_code=201)
    async def create_plan(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        plan = TenantPlan(**body)
        db.add(plan)
        await db.commit()
        await db.refresh(plan)
        return plan

    # ── Platform Stats ────────────────────────────────────────
    @router.get("/platform/stats", summary="Platform-wide SaaS statistics")
    async def platform_stats(db: AsyncSession = Depends(_get_db)):
        total_tenants = (await db.execute(select(func.count(Tenant.id)))).scalar()
        active_tenants = (await db.execute(select(func.count(Tenant.id)).where(Tenant.is_active == True))).scalar()
        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "platform_status": "healthy"
        }

    return router


