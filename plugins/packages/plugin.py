"""
NetverseIQ Plugin: Packages & Plans
Defines internet service plans (e.g. 5Mbps, 10Mbps).
"""
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from datetime import datetime
from typing import List, Optional

def register(app: FastAPI, Base) -> None:

    # ── Models ────────────────────────────────────────────────
    from sqlalchemy import Integer, String, Text, DateTime, Float, Boolean
    from sqlalchemy.orm import Mapped, mapped_column

    class Package(Base):
        __tablename__ = "isp_packages"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
        speed_mbps: Mapped[int] = mapped_column(Integer, nullable=False) # e.g. 5, 10, 20
        price: Mapped[float] = mapped_column(Float, nullable=False)
        description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        
        # Technical details (for future MikroTik integration)
        upload_limit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True) # e.g. "5M"
        download_limit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True) # e.g. "5M"
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Routes ────────────────────────────────────────────────
    from database import get_db

    router = APIRouter(prefix="/api/p/packages", tags=["Plugin: Packages"])

    def _clean(obj):
        if not obj: return None
        d = obj.__dict__.copy()
        d.pop("_sa_instance_state", None)
        return d

    @router.get("/list", summary="List all packages")
    async def list_packages(
        db: AsyncSession = Depends(get_db),
    ):
        result = await db.execute(select(Package).order_by(Package.price.asc()))
        return [_clean(r) for r in result.scalars().all()]

    @router.post("/add", status_code=201, summary="Create a new package")
    async def create_package(body: dict, db: AsyncSession = Depends(get_db)):
        if not body.get("name") or not body.get("price") or not body.get("speed_mbps"):
            raise HTTPException(400, "Name, Price, and Speed are required")
        
        # Check if name exists
        existing = await db.execute(select(Package).where(Package.name == body["name"]))
        if existing.scalar_one_or_none():
            raise HTTPException(400, f"Package '{body['name']}' already exists")

        pkg = Package(**body)
        db.add(pkg)
        await db.commit()
        await db.refresh(pkg)
        return _clean(pkg)

    @router.put("/{pkg_id}", summary="Update package details")
    async def update_package(pkg_id: int, body: dict, db: AsyncSession = Depends(get_db)):
        body.pop("id", None)
        body.pop("created_at", None)
        body.pop("updated_at", None)
        
        await db.execute(
            update(Package).where(Package.id == pkg_id).values(**body)
        )
        await db.commit()
        
        result = await db.execute(select(Package).where(Package.id == pkg_id))
        return _clean(result.scalar_one_or_none())

    @router.delete("/{pkg_id}", status_code=204)
    async def delete_package(pkg_id: int, db: AsyncSession = Depends(get_db)):
        await db.execute(delete(Package).where(Package.id == pkg_id))
        await db.commit()

    app.include_router(router)
