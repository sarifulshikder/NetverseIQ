"""Reseller Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from datetime import datetime

router = APIRouter(prefix="/api/p/reseller", tags=["Plugin: Reseller"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    Reseller = models["Reseller"]
    ResellerCustomer = models["ResellerCustomer"]
    ResellerWallet = models["ResellerWallet"]

    # ── Reseller Endpoints ────────────────────────────────────
    @router.get("/", summary="List all resellers")
    async def list_resellers(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Reseller).options(selectinload(Reseller.wallet)))
        return result.scalars().all()

    @router.post("/", status_code=201)
    async def create_reseller(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        reseller = Reseller(**body)
        db.add(reseller)
        await db.flush() # Get ID
        
        # Initialize wallet
        wallet = ResellerWallet(reseller_id=reseller.id, balance=0.0)
        db.add(wallet)
        
        await db.commit()
        await db.refresh(reseller)
        return reseller

    # ── Wallet Endpoints ──────────────────────────────────────
    @router.post("/{reseller_id}/wallet/recharge", summary="Recharge reseller wallet")
    async def recharge_wallet(reseller_id: int, amount: float, db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(ResellerWallet).where(ResellerWallet.reseller_id == reseller_id))
        wallet = result.scalar_one_or_none()
        if not wallet:
            raise HTTPException(404, "Reseller wallet not found")
        
        wallet.balance += amount
        await db.commit()
        await db.refresh(wallet)
        return wallet

    # ── Customer Endpoints ────────────────────────────────────
    @router.get("/{reseller_id}/customers", summary="List reseller customers")
    async def list_reseller_customers(reseller_id: int, db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(ResellerCustomer).where(ResellerCustomer.reseller_id == reseller_id))
        return result.scalars().all()

    @router.post("/{reseller_id}/customers", status_code=201)
    async def assign_customer(reseller_id: int, customer_id: int, db: AsyncSession = Depends(_get_db)):
        mapping = ResellerCustomer(reseller_id=reseller_id, customer_id=customer_id)
        db.add(mapping)
        await db.commit()
        return mapping

    return router


