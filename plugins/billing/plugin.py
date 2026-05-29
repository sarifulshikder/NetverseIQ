"""
NetverseIQ Plugin: Billing & Invoicing
Registers Invoice/Payment models and API routes.
"""
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime


def register(app: FastAPI, Base) -> None:

    # ── Models ────────────────────────────────────────────────
    from sqlalchemy import Integer, String, Float, Text, DateTime, ForeignKey
    from sqlalchemy.orm import Mapped, mapped_column

    class Invoice(Base):
        __tablename__ = "invoices"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        invoice_number: Mapped[str] = mapped_column(String(64), unique=True, index=True)
        customer_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
        customer_name: Mapped[str] = mapped_column(String(256), default="")
        amount: Mapped[float] = mapped_column(Float, default=0.0)
        discount: Mapped[float] = mapped_column(Float, default=0.0)
        tax: Mapped[float] = mapped_column(Float, default=0.0)
        total: Mapped[float] = mapped_column(Float, default=0.0)
        status: Mapped[str] = mapped_column(String(32), default="unpaid")  # unpaid/paid/partial/cancelled
        due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
        paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
        payment_method: Mapped[str] = mapped_column(String(64), default="")
        notes: Mapped[str] = mapped_column(Text, default="")
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Routes ────────────────────────────────────────────────
    from database import get_db
    import random, string

    router = APIRouter(prefix="/api/p/billing", tags=["Plugin: Billing"])

    def _clean(obj):
        d = obj.__dict__.copy()
        d.pop("_sa_instance_state", None)
        return d

    def gen_invoice_number():
        suffix = ''.join(random.choices(string.digits, k=6))
        return f"INV-{datetime.utcnow().strftime('%Y%m')}-{suffix}"

    @router.get("/invoices", summary="List invoices")
    async def list_invoices(
        skip: int = 0, limit: int = 50, status: str = "",
        db: AsyncSession = Depends(get_db),
    ):
        q = select(Invoice)
        if status:
            q = q.where(Invoice.status == status)
        result = await db.execute(q.offset(skip).limit(limit))
        items = [_clean(r) for r in result.scalars().all()]
        total = (await db.execute(select(func.count(Invoice.id)))).scalar()
        return {"total": total, "items": items}

    @router.get("/stats", summary="Billing statistics")
    async def billing_stats(db: AsyncSession = Depends(get_db)):
        total_invoices = (await db.execute(select(func.count(Invoice.id)))).scalar()
        paid = (await db.execute(select(func.count(Invoice.id)).where(Invoice.status == "paid"))).scalar()
        unpaid = (await db.execute(select(func.count(Invoice.id)).where(Invoice.status == "unpaid"))).scalar()
        total_revenue = (await db.execute(select(func.sum(Invoice.total)).where(Invoice.status == "paid"))).scalar() or 0
        pending_amount = (await db.execute(select(func.sum(Invoice.total)).where(Invoice.status == "unpaid"))).scalar() or 0
        return {
            "total_invoices": total_invoices,
            "paid": paid,
            "unpaid": unpaid,
            "total_revenue": round(total_revenue, 2),
            "pending_amount": round(pending_amount, 2),
        }

    @router.post("/invoices", status_code=201, summary="Create invoice")
    async def create_invoice(body: dict, db: AsyncSession = Depends(get_db)):
        body.pop("id", None)
        if not body.get("invoice_number"):
            body["invoice_number"] = gen_invoice_number()
        amount = body.get("amount", 0)
        discount = body.get("discount", 0)
        tax = body.get("tax", 0)
        body["total"] = round(amount - discount + tax, 2)
        inv = Invoice(**body)
        db.add(inv)
        await db.commit()
        await db.refresh(inv)
        return _clean(inv)

    @router.get("/invoices/{invoice_id}", summary="Get invoice")
    async def get_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
        r = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
        inv = r.scalar_one_or_none()
        if not inv:
            raise HTTPException(404, "Invoice not found")
        return _clean(inv)

    @router.put("/invoices/{invoice_id}", summary="Update invoice")
    async def update_invoice(invoice_id: int, body: dict, db: AsyncSession = Depends(get_db)):
        r = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
        inv = r.scalar_one_or_none()
        if not inv:
            raise HTTPException(404, "Invoice not found")
        for k, v in body.items():
            if hasattr(inv, k) and k not in ("id", "created_at"):
                setattr(inv, k, v)
        if body.get("status") == "paid" and not inv.paid_at:
            inv.paid_at = datetime.utcnow()
        await db.commit()
        await db.refresh(inv)
        return _clean(inv)

    @router.delete("/invoices/{invoice_id}", status_code=204, summary="Delete invoice")
    async def delete_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
        r = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
        inv = r.scalar_one_or_none()
        if not inv:
            raise HTTPException(404, "Invoice not found")
        await db.delete(inv)
        await db.commit()

    app.include_router(router)
