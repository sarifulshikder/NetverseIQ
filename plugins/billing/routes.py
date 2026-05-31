"""Billing Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from datetime import datetime
import random
import string

from api.deps import get_current_user
from models.user import User

router = APIRouter(prefix="/api/p/billing", tags=["Plugin: Billing"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    Invoice = models["Invoice"]
    InvoiceItem = models["InvoiceItem"]
    CreditNote = models["CreditNote"]
    ProformaInvoice = models["ProformaInvoice"]

    def gen_invoice_number():
        suffix = ''.join(random.choices(string.digits, k=6))
        return f"INV-{datetime.utcnow().strftime('%Y%m')}-{suffix}"

    # ── Invoice Endpoints ─────────────────────────────────────
    @router.get("/invoices", summary="List all invoices")
    async def list_invoices(
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        customer_id: Optional[int] = None,
        db: AsyncSession = Depends(_get_db),
        current_user: User = Depends(get_current_user),
    ):
        query = select(Invoice)
        if status:
            query = query.where(Invoice.status == status)
        if customer_id:
            query = query.where(Invoice.customer_id == customer_id)
            
        result = await db.execute(query.offset(skip).limit(limit).order_by(Invoice.created_at.desc()))
        items = result.scalars().all()
        total = (await db.execute(select(func.count(Invoice.id)))).scalar()
        return {"total": total, "items": items}

    @router.post("/invoices", status_code=status.HTTP_201_CREATED, summary="Create invoice")
    async def create_invoice(
        body: Dict[str, Any], 
        db: AsyncSession = Depends(_get_db),
        current_user: User = Depends(get_current_user),
    ):
        items_data = body.pop("items", [])
        
        if not body.get("invoice_number"):
            body["invoice_number"] = gen_invoice_number()
            
        # Handle enum
        from billing.models import InvoiceStatus
        if "status" in body and isinstance(body["status"], str):
            body["status"] = InvoiceStatus(body["status"])

        invoice = Invoice(**body)
        db.add(invoice)
        await db.flush() # Get invoice.id
        
        # Add items
        sub_total = 0
        for item_data in items_data:
            item_total = item_data.get("quantity", 1) * item_data.get("unit_price", 0)
            sub_total += item_total
            item = InvoiceItem(invoice_id=invoice.id, total=item_total, **item_data)
            db.add(item)
            
        invoice.sub_total = sub_total
        # Calculate final total if not provided (roadmap: total = sub - discount + tax)
        discount = body.get("discount", 0)
        tax_amount = body.get("tax_amount", 0)
        invoice.total = sub_total - discount + tax_amount
        
        await db.commit()
        await db.refresh(invoice)
        return invoice

    @router.get("/stats", summary="Billing statistics")
    async def billing_stats(
        db: AsyncSession = Depends(_get_db),
        current_user: User = Depends(get_current_user),
    ):
        total_invoices = (await db.execute(select(func.count(Invoice.id)))).scalar()
        paid = (await db.execute(select(func.count(Invoice.id)).where(Invoice.status == "paid"))).scalar()
        unpaid = (await db.execute(select(func.count(Invoice.id)).where(Invoice.status == "unpaid"))).scalar()
        overdue = (await db.execute(select(func.count(Invoice.id)).where(Invoice.status == "overdue"))).scalar()
        
        total_revenue = (await db.execute(select(func.sum(Invoice.total)).where(Invoice.status == "paid"))).scalar() or 0
        outstanding = (await db.execute(select(func.sum(Invoice.total)).where(Invoice.status == "unpaid"))).scalar() or 0
        
        return {
            "total_invoices": total_invoices,
            "paid": paid,
            "unpaid": unpaid,
            "overdue": overdue,
            "total_revenue": round(total_revenue, 2),
            "outstanding": round(outstanding, 2),
            "collection_efficiency": round((total_revenue / (total_revenue + outstanding) * 100), 2) if (total_revenue + outstanding) > 0 else 0
        }

    @router.get("/invoices/{invoice_id}", summary="Get invoice by ID")
    async def get_invoice(
        invoice_id: int, 
        db: AsyncSession = Depends(_get_db),
        current_user: User = Depends(get_current_user),
    ):
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(Invoice)
            .where(Invoice.id == invoice_id)
            .options(selectinload(Invoice.items))
        )
        inv = result.scalar_one_or_none()
        if not inv:
            raise HTTPException(404, "Invoice not found")
        return inv

    @router.get("/invoices/{invoice_id}/pdf", summary="Generate Invoice PDF")
    async def get_invoice_pdf(
        invoice_id: int,
        current_user: User = Depends(get_current_user),
    ):
        # Placeholder for actual PDF generation
        return {"status": "success", "message": f"PDF generated for invoice {invoice_id} (mock)"}

    return router


