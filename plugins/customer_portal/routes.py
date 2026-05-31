"""Customer Portal Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from datetime import datetime, timedelta
from jose import jwt, JWTError
from config import settings

router = APIRouter(prefix="/api/p/customer_portal", tags=["Plugin: Customer_Portal"])

# Models will be injected via get_router
models = {}

async def get_current_portal_customer(
    request: Request,
    db: AsyncSession = Depends(_get_db)
):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("role") != "customer":
            raise HTTPException(status_code=403, detail="Forbidden: Not a customer")
        
        customer_id = int(payload.get("sub"))
        # We need the Customer model. It's usually injected or we can import it if we know the path.
        # Since this is a plugin, we'll use the injected models if available, or query directly.
        from plugins.customer.models import Customer
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        customer = result.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=401, detail="Customer not found")
        return customer
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    # ── Auth Endpoints ────────────────────────────────────────
    @router.post("/login", summary="Customer portal login (Mock)")
    async def portal_login(phone: str, db: AsyncSession = Depends(_get_db)):
        from plugins.customer.models import Customer
        result = await db.execute(select(Customer).where(Customer.phone == phone))
        customer = result.scalar_one_or_none()
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer with this phone not found")
        
        # In a real app, send OTP here. For mock, we just issue token.
        expire = datetime.utcnow() + timedelta(days=7)
        token = jwt.encode(
            {"sub": str(customer.id), "role": "customer", "exp": expire},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return {
            "status": "success", 
            "access_token": token,
            "token_type": "bearer",
            "customer_name": customer.name
        }

    # ── Dashboard Endpoints ────────────────────────────────────
    @router.get("/dashboard", summary="Customer portal dashboard summary")
    async def portal_dashboard(
        db: AsyncSession = Depends(_get_db), 
        current_customer: Any = Depends(get_current_portal_customer)
    ):
        # Use real data from current_customer
        return {
            "customer_name": current_customer.name,
            "current_package": current_customer.package_name or "No Package",
            "status": current_customer.status,
            "total_due": float(current_customer.monthly_fee), # Simplified
            "expiry_date": (datetime.utcnow() + timedelta(days=15)).strftime("%Y-%m-%d"), # Mock expiry
            "data_usage": "Usage data requires RADIUS integration"
        }

    # ── Billing Endpoints ─────────────────────────────────────
    @router.get("/invoices", summary="Customer invoices")
    async def portal_invoices(
        db: AsyncSession = Depends(_get_db), 
        current_customer: Any = Depends(get_current_portal_customer)
    ):
        try:
            from plugins.billing.models import Invoice
            result = await db.execute(
                select(Invoice).where(Invoice.customer_id == current_customer.id).order_by(Invoice.created_at.desc())
            )
            return result.scalars().all()
        except ImportError:
            return []

    # ── Support Endpoints ─────────────────────────────────────
    @router.get("/tickets", summary="Customer tickets")
    async def portal_tickets(
        db: AsyncSession = Depends(_get_db), 
        current_customer: Any = Depends(get_current_portal_customer)
    ):
        try:
            from plugins.support.models import Ticket
            result = await db.execute(
                select(Ticket).where(Ticket.customer_id == current_customer.id).order_by(Ticket.created_at.desc())
            )
            return result.scalars().all()
        except ImportError:
            return []

    return router


