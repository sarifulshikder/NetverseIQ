"""Payment Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/p/payment", tags=["Plugin: Payment"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    Payment = models["Payment"]
    AdvancePayment = models["AdvancePayment"]
    Refund = models["Refund"]

    # ── Payment Endpoints ─────────────────────────────────────
    @router.get("/", summary="List all payments")
    async def list_payments(
        skip: int = 0,
        limit: int = 50,
        customer_id: Optional[int] = None,
        db: AsyncSession = Depends(_get_db),
    ):
        query = select(Payment)
        if customer_id:
            query = query.where(Payment.customer_id == customer_id)
        result = await db.execute(query.offset(skip).limit(limit).order_by(Payment.created_at.desc()))
        items = result.scalars().all()
        total = (await db.execute(select(func.count(Payment.id)))).scalar()
        return {"total": total, "items": items}

    @router.post("/", status_code=status.HTTP_201_CREATED, summary="Process payment")
    async def process_payment(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        # Handle invoice linking logic
        invoice_id = body.get("invoice_id")
        
        payment = Payment(**body)
        db.add(payment)
        
        if invoice_id:
            # Mark invoice as paid (if billing plugin is loaded)
            # This would ideally be handled via event bus, 
            # but for now we'll do a direct update if we can
            try:
                from plugins.billing.models import Invoice, InvoiceStatus
                result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
                invoice = result.scalar_one_or_none()
                if invoice:
                    invoice.status = InvoiceStatus.paid
                    invoice.paid_at = datetime.utcnow()
                    invoice.payment_method = body.get("method", "other")
            except ImportError:
                pass # Billing plugin not loaded or models different
        
        await db.commit()
        await db.refresh(payment)
        
        # Log activity
        from core.services.activity_service import log_activity
        await log_activity(db, "payment.received", resource=f"payment:{payment.id}", detail=f"Received payment of {payment.amount} via {payment.method}")
        await db.commit()
        
        return payment

    @router.get("/stats", summary="Payment statistics")
    async def payment_stats(db: AsyncSession = Depends(_get_db)):
        total_collected = (await db.execute(select(func.sum(Payment.amount)))).scalar() or 0
        
        # Breakdown by method
        method_stats_query = select(Payment.method, func.sum(Payment.amount)).group_by(Payment.method)
        method_stats = (await db.execute(method_stats_query)).all()
        
        return {
            "total_collected": round(total_collected, 2),
            "method_breakdown": {method: round(amount, 2) for method, amount in method_stats}
        }

    # ── Refund Endpoints ──────────────────────────────────────
    @router.post("/refunds", status_code=201)
    async def request_refund(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        refund = Refund(**body)
        db.add(refund)
        await db.commit()
        await db.refresh(refund)
        return refund

    return router


def _get_db():
    from database import get_db
    return Depends(get_db)
