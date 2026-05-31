"""Network Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from datetime import datetime

router = APIRouter(prefix="/api/p/network", tags=["Plugin: Network"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    NASDevice = models["NASDevice"]
    NetworkNode = models["NetworkNode"]
    IPPool = models["IPPool"]
    IPAssignment = models["IPAssignment"]
    NetworkLink = models["NetworkLink"]
    NetworkOutage = models["NetworkOutage"]

    # ── NAS Device Endpoints ──────────────────────────────────
    @router.get("/nas", summary="List all NAS devices")
    async def list_nas(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(NASDevice))
        return result.scalars().all()

    @router.post("/nas", status_code=201)
    async def create_nas(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        nas = NASDevice(**body)
        db.add(nas)
        await db.commit()
        await db.refresh(nas)
        return nas

    @router.get("/nas/{nas_id}/test", summary="Test NAS connection")
    async def test_nas_connection(nas_id: int, db: AsyncSession = Depends(_get_db)):
        # Placeholder for actual MikroTik/SNMP test
        return {"status": "success", "message": f"Connection to NAS {nas_id} successful (mock)"}

    # ── IP Pool Endpoints ─────────────────────────────────────
    @router.get("/ip-pools", summary="List all IP pools")
    async def list_ip_pools(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(IPPool))
        return result.scalars().all()

    @router.post("/ip-pools", status_code=201)
    async def create_ip_pool(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        pool = IPPool(**body)
        db.add(pool)
        await db.commit()
        await db.refresh(pool)
        return pool

    @router.get("/ip-pools/{pool_id}/stats", summary="IP pool usage stats")
    async def ip_pool_stats(pool_id: int, db: AsyncSession = Depends(_get_db)):
        total_assignments = (await db.execute(
            select(func.count(IPAssignment.id)).where(IPAssignment.pool_id == pool_id)
        )).scalar()
        return {"pool_id": pool_id, "used_ips": total_assignments}

    # ── Network Node Endpoints ────────────────────────────────
    @router.get("/nodes", summary="List all network nodes")
    async def list_nodes(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(NetworkNode))
        return result.scalars().all()

    @router.post("/nodes", status_code=201)
    async def create_node(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        node = NetworkNode(**body)
        db.add(node)
        await db.commit()
        await db.refresh(node)
        return node

    # ── Outage Endpoints ──────────────────────────────────────
    @router.get("/outages", summary="List all outages")
    async def list_outages(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(NetworkOutage).order_by(NetworkOutage.start_time.desc()))
        return result.scalars().all()

    @router.post("/outages", status_code=201)
    async def report_outage(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        outage = NetworkOutage(**body)
        db.add(outage)
        await db.commit()
        await db.refresh(outage)
        return outage

    @router.put("/outages/{outage_id}/resolve", summary="Resolve outage")
    async def resolve_outage(outage_id: int, db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(NetworkOutage).where(NetworkOutage.id == outage_id))
        outage = result.scalar_one_or_none()
        if not outage:
            raise HTTPException(404, "Outage not found")
        outage.status = "resolved"
        outage.end_time = datetime.utcnow()
        await db.commit()
        await db.refresh(outage)
        return outage

    return router


