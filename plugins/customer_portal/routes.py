"""Customer Portal Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from api.deps import get_current_user
from models.user import User
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/p/customer_portal", tags=["Plugin: Customer_Portal"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    # ── Auth Endpoints ────────────────────────────────────────
    @router.post("/login", summary="Customer portal login (OTP mock)")
    async def portal_login(phone: str, current_user: User = Depends(get_current_user)):
        # Mock OTP login
        return {"status": "success", "message": "OTP sent to your phone"}

    # ── Dashboard Endpoints ────────────────────────────────────
    @router.get("/dashboard/{customer_id}", summary="Customer portal dashboard summary")
    async def portal_dashboard(customer_id: int, db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        # Mock data aggregating from other plugins
        return {
            "customer_name": "John Doe",
            "current_package": "Home Ultra 10Mbps",
            "status": "active",
            "total_due": 1200.0,
            "expiry_date": "2024-06-30",
            "data_usage": "145 GB / Unlimited"
        }

    # ── Billing Endpoints ─────────────────────────────────────
    @router.get("/invoices/{customer_id}", summary="Customer invoices")
    async def portal_invoices(customer_id: int, db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        # In a real app, we'd query billing.Invoice table
        return [
            {"id": 101, "invoice_no": "INV-202405-01", "amount": 1200, "status": "unpaid", "date": "2024-05-01"},
            {"id": 100, "invoice_no": "INV-202404-99", "amount": 1200, "status": "paid", "date": "2024-04-01"}
        ]

    # ── Support Endpoints ─────────────────────────────────────
    @router.get("/tickets/{customer_id}", summary="Customer tickets")
    async def portal_tickets(customer_id: int, db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        return [
            {"id": 50, "subject": "Slow internet speed", "status": "open", "date": "2024-05-28"}
        ]

    return router


