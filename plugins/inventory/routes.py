"""Inventory Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from datetime import datetime

router = APIRouter(prefix="/api/p/inventory", tags=["Plugin: Inventory"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    Product = models["Product"]
    ProductCategory = models["ProductCategory"]
    Warehouse = models["Warehouse"]
    Stock = models["Stock"]
    StockMovement = models["StockMovement"]
    EquipmentAssignment = models["EquipmentAssignment"]

    # ── Product Endpoints ─────────────────────────────────────
    @router.get("/products", summary="List all products")
    async def list_products(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Product).options(selectinload(Product.category)))
        return result.scalars().all()

    @router.post("/products", status_code=201)
    async def create_product(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        product = Product(**body)
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product

    # ── Stock Endpoints ───────────────────────────────────────
    @router.get("/stock", summary="List stock levels")
    async def list_stock(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Stock).options(selectinload(Stock.product), selectinload(Stock.warehouse)))
        return result.scalars().all()

    @router.post("/stock/move", status_code=201)
    async def move_stock(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        from .models import StockAction
        product_id = body["product_id"]
        warehouse_id = body["warehouse_id"]
        quantity = body["quantity"]
        action = StockAction(body["action"])
        
        # Update Stock table
        result = await db.execute(
            select(Stock).where(Stock.product_id == product_id, Stock.warehouse_id == warehouse_id)
        )
        stock = result.scalar_one_or_none()
        
        if not stock:
            stock = Stock(product_id=product_id, warehouse_id=warehouse_id, quantity=0)
            db.add(stock)
            
        if action == StockAction.stock_in:
            stock.quantity += quantity
        elif action == StockAction.stock_out:
            if stock.quantity < quantity:
                raise HTTPException(400, "Insufficient stock")
            stock.quantity -= quantity
            
        # Log movement
        movement = StockMovement(**body)
        db.add(movement)
        
        await db.commit()
        await db.refresh(stock)
        return stock

    # ── Assignment Endpoints ──────────────────────────────────
    @router.post("/assignments", status_code=201)
    async def assign_equipment(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        assignment = EquipmentAssignment(**body)
        db.add(assignment)
        
        # Deduct from stock (Mock logic - assuming primary warehouse ID 1)
        # In real app, we'd specify which warehouse it's coming from
        await db.commit()
        await db.refresh(assignment)
        return assignment

    @router.get("/stats", summary="Inventory statistics")
    async def inventory_stats(db: AsyncSession = Depends(_get_db)):
        total_products = (await db.execute(select(func.count(Product.id)))).scalar()
        low_stock = (await db.execute(
            select(func.count(Stock.id)).join(Product).where(Stock.quantity <= Product.min_stock_level)
        )).scalar()
        
        return {
            "total_products": total_products,
            "low_stock_alerts": low_stock
        }

    return router


