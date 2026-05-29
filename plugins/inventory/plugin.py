"""
NetverseIQ Plugin: Inventory & Asset Management
Manages hardware inventory like ONU, Routers, Cables.
"""
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from datetime import datetime
from typing import List, Optional
import enum

def register(app: FastAPI, Base) -> None:

    # ── Models ────────────────────────────────────────────────
    from sqlalchemy import Integer, String, Text, DateTime, Float, Enum as SQLEnum
    from sqlalchemy.orm import Mapped, mapped_column

    class AssetStatus(str, enum.Enum):
        in_stock = "in_stock"
        deployed = "deployed"
        faulty = "faulty"
        lost = "lost"

    class InventoryItem(Base):
        __tablename__ = "inventory_items"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(256), nullable=False) # e.g. Tenda F3, Huawei ONU
        category: Mapped[str] = mapped_column(String(64), default="general") # ONU, Router, Cable, Splitter
        serial_number: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
        mac_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
        status: Mapped[AssetStatus] = mapped_column(SQLEnum(AssetStatus), default=AssetStatus.in_stock)
        
        # Deployment details
        customer_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)
        customer_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        location: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        
        purchase_price: Mapped[float] = mapped_column(Float, default=0.0)
        supplier: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Routes ────────────────────────────────────────────────
    from database import get_db

    router = APIRouter(prefix="/api/p/inventory", tags=["Plugin: Inventory"])

    def _clean(obj):
        if not obj: return None
        d = obj.__dict__.copy()
        d.pop("_sa_instance_state", None)
        return d

    @router.get("/items", summary="List inventory items")
    async def list_items(
        skip: int = 0, limit: int = 50, 
        status: Optional[AssetStatus] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        db: AsyncSession = Depends(get_db),
    ):
        q = select(InventoryItem)
        if status:
            q = q.where(InventoryItem.status == status)
        if category:
            q = q.where(InventoryItem.category == category)
        if search:
            q = q.where(
                (InventoryItem.name.ilike(f"%{search}%")) | 
                (InventoryItem.serial_number.ilike(f"%{search}%")) |
                (InventoryItem.customer_name.ilike(f"%{search}%"))
            )
        
        q = q.order_by(InventoryItem.updated_at.desc())
        
        result = await db.execute(q.offset(skip).limit(limit))
        items = [_clean(r) for r in result.scalars().all()]
        
        # Count for pagination
        count_q = select(func.count(InventoryItem.id))
        if status: count_q = count_q.where(InventoryItem.status == status)
        if category: count_q = count_q.where(InventoryItem.category == category)
        if search: count_q = count_q.where(
            (InventoryItem.name.ilike(f"%{search}%")) | 
            (InventoryItem.serial_number.ilike(f"%{search}%"))
        )
        total = (await db.execute(count_q)).scalar()
        
        return {"total": total, "items": items}

    @router.post("/items", status_code=201, summary="Add item to inventory")
    async def create_item(body: dict, db: AsyncSession = Depends(get_db)):
        if not body.get("name") or not body.get("serial_number"):
            raise HTTPException(400, "Name and Serial Number are required")
        
        # Check uniqueness manually since we want a nice error
        existing = await db.execute(select(InventoryItem).where(InventoryItem.serial_number == body["serial_number"]))
        if existing.scalar_one_or_none():
            raise HTTPException(400, f"Serial number {body['serial_number']} already exists")

        item = InventoryItem(**body)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return _clean(item)

    @router.get("/items/{item_id}", summary="Get item details")
    async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(404, "Item not found")
        return _clean(item)

    @router.put("/items/{item_id}", summary="Update inventory item")
    async def update_item(item_id: int, body: dict, db: AsyncSession = Depends(get_db)):
        body.pop("id", None)
        body.pop("created_at", None)
        body.pop("updated_at", None)
        
        await db.execute(
            update(InventoryItem).where(InventoryItem.id == item_id).values(**body)
        )
        await db.commit()
        
        result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
        return _clean(result.scalar_one_or_none())

    @router.delete("/items/{item_id}", status_code=204)
    async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
        await db.execute(delete(InventoryItem).where(InventoryItem.id == item_id))
        await db.commit()

    @router.get("/stats", summary="Inventory statistics")
    async def inventory_stats(db: AsyncSession = Depends(get_db)):
        total = (await db.execute(select(func.count(InventoryItem.id)))).scalar()
        in_stock = (await db.execute(select(func.count(InventoryItem.id)).where(InventoryItem.status == AssetStatus.in_stock))).scalar()
        deployed = (await db.execute(select(func.count(InventoryItem.id)).where(InventoryItem.status == AssetStatus.deployed))).scalar()
        faulty = (await db.execute(select(func.count(InventoryItem.id)).where(InventoryItem.status == AssetStatus.faulty))).scalar()
        
        # Value of stock
        stock_value = (await db.execute(select(func.sum(InventoryItem.purchase_price)).where(InventoryItem.status == AssetStatus.in_stock))).scalar() or 0
        
        return {
            "total_items": total,
            "in_stock": in_stock,
            "deployed": deployed,
            "faulty": faulty,
            "stock_value": round(stock_value, 2)
        }

    app.include_router(router)
