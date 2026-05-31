"""Packages Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from datetime import datetime

router = APIRouter(prefix="/api/p/packages", tags=["Plugin: Packages"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    Package = models["Package"]
    PackageCategory = models["PackageCategory"]
    PackagePromotion = models["PackagePromotion"]
    PackageAddon = models["PackageAddon"]

    # ── Package Endpoints ─────────────────────────────────────
    @router.get("/", summary="List all packages")
    async def list_packages(
        db: AsyncSession = Depends(_get_db),
    ):
        result = await db.execute(select(Package).order_by(Package.price.asc()))
        return result.scalars().all()

    @router.post("/", status_code=status.HTTP_201_CREATED, summary="Create package")
    async def create_package(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        pkg = Package(**body)
        db.add(pkg)
        await db.commit()
        await db.refresh(pkg)
        return pkg

    @router.get("/stats", summary="Package statistics")
    async def package_stats(db: AsyncSession = Depends(_get_db)):
        total = (await db.execute(select(func.count(Package.id)))).scalar()
        active = (await db.execute(select(func.count(Package.id)).where(Package.is_active == True))).scalar()
        
        # Breakdown by category
        cat_stats_query = select(PackageCategory.name, func.count(Package.id)).join(Package).group_by(PackageCategory.name)
        cat_stats = (await db.execute(cat_stats_query)).all()
        
        return {
            "total": total,
            "active": active,
            "category_breakdown": {cat: count for cat, count in cat_stats}
        }

    @router.get("/{pkg_id}", summary="Get package by ID")
    async def get_package(pkg_id: int, db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Package).where(Package.id == pkg_id))
        pkg = result.scalar_one_or_none()
        if not pkg:
            raise HTTPException(404, "Package not found")
        return pkg

    @router.put("/{pkg_id}", summary="Update package")
    async def update_package(pkg_id: int, body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Package).where(Package.id == pkg_id))
        pkg = result.scalar_one_or_none()
        if not pkg:
            raise HTTPException(404, "Package not found")
        for k, v in body.items():
            if hasattr(pkg, k) and k not in ("id", "created_at"):
                setattr(pkg, k, v)
        await db.commit()
        await db.refresh(pkg)
        return pkg

    @router.delete("/{pkg_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_package(pkg_id: int, db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Package).where(Package.id == pkg_id))
        pkg = result.scalar_one_or_none()
        if not pkg:
            raise HTTPException(404, "Package not found")
        await db.delete(pkg)
        await db.commit()

    # ── Category Endpoints ────────────────────────────────────
    @router.get("/categories", summary="List package categories")
    async def list_categories(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(PackageCategory))
        return result.scalars().all()

    @router.post("/categories", status_code=201)
    async def create_category(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        cat = PackageCategory(**body)
        db.add(cat)
        await db.commit()
        await db.refresh(cat)
        return cat

    # ── Promotion Endpoints ───────────────────────────────────
    @router.get("/promotions", summary="List promotions")
    async def list_promotions(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(PackagePromotion))
        return result.scalars().all()

    @router.post("/promotions", status_code=201)
    async def create_promotion(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        promo = PackagePromotion(**body)
        db.add(promo)
        await db.commit()
        await db.refresh(promo)
        return promo

    return router


