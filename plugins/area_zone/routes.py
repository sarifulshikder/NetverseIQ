"""Area Zone Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db as _get_db
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/api/p/area_zone", tags=["Plugin: Area_Zone"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    Area = models["Area"]
    Zone = models["Zone"]
    ZoneAssignment = models["ZoneAssignment"]

    # ── Area Endpoints ────────────────────────────────────────
    @router.get("/areas", summary="List all areas")
    async def list_areas(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Area))
        return result.scalars().all()

    @router.post("/areas", status_code=201)
    async def create_area(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        area = Area(**body)
        db.add(area)
        await db.commit()
        await db.refresh(area)
        return area

    # ── Zone Endpoints ────────────────────────────────────────
    @router.get("/zones", summary="List all zones")
    async def list_zones(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Zone))
        return result.scalars().all()

    @router.post("/zones", status_code=201)
    async def create_zone(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        zone = Zone(**body)
        db.add(zone)
        await db.commit()
        await db.refresh(zone)
        return zone

    @router.get("/zones/stats", summary="Zone statistics")
    async def zone_stats(db: AsyncSession = Depends(_get_db)):
        # This is a placeholder, actual stats would join with customers
        total_zones = (await db.execute(select(func.count(Zone.id)))).scalar()
        total_areas = (await db.execute(select(func.count(Area.id)))).scalar()
        return {
            "total_areas": total_areas,
            "total_zones": total_zones
        }

    return router


