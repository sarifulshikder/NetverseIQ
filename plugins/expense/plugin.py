"""
NetverseIQ Plugin: Expense & Accounts
Tracks business expenses like Rent, Salary, Bandwidth, etc.
"""
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from datetime import datetime
from typing import List, Optional
import enum

def register(app: FastAPI, Base) -> None:

    # ── Models ────────────────────────────────────────────────
    from sqlalchemy import Integer, String, Text, DateTime, Float
    from sqlalchemy.orm import Mapped, mapped_column

    class Expense(Base):
        __tablename__ = "expenses"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        title: Mapped[str] = mapped_column(String(256), nullable=False)
        category: Mapped[str] = mapped_column(String(64), default="general") # Rent, Salary, Bandwidth, Utility, etc.
        amount: Mapped[float] = mapped_column(Float, default=0.0)
        date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        payment_method: Mapped[str] = mapped_column(String(64), default="Cash") # Cash, Bank, BKash
        reference: Mapped[Optional[str]] = mapped_column(String(128), nullable=True) # Bill/Voucher ID
        description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Routes ────────────────────────────────────────────────
    from database import get_db

    router = APIRouter(prefix="/api/p/expense", tags=["Plugin: Expense"])

    def _clean(obj):
        if not obj: return None
        d = obj.__dict__.copy()
        d.pop("_sa_instance_state", None)
        return d

    @router.get("/list", summary="List expenses")
    async def list_expenses(
        skip: int = 0, limit: int = 50, 
        category: Optional[str] = None,
        db: AsyncSession = Depends(get_db),
    ):
        q = select(Expense)
        if category:
            q = q.where(Expense.category == category)
        
        q = q.order_by(Expense.date.desc())
        
        result = await db.execute(q.offset(skip).limit(limit))
        items = [_clean(r) for r in result.scalars().all()]
        
        count_q = select(func.count(Expense.id))
        if category: count_q = count_q.where(Expense.category == category)
        total = (await db.execute(count_q)).scalar()
        
        return {"total": total, "items": items}

    @router.post("/add", status_code=201, summary="Add expense record")
    async def create_expense(body: dict, db: AsyncSession = Depends(get_db)):
        if not body.get("title") or not body.get("amount"):
            raise HTTPException(400, "Title and Amount are required")
        
        # Convert date string to datetime if provided
        if body.get("date") and isinstance(body["date"], str):
            try:
                body["date"] = datetime.fromisoformat(body["date"].replace("Z", ""))
            except:
                body["date"] = datetime.utcnow()

        expense = Expense(**body)
        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        return _clean(expense)

    @router.delete("/{expense_id}", status_code=204)
    async def delete_expense(expense_id: int, db: AsyncSession = Depends(get_db)):
        await db.execute(delete(Expense).where(Expense.id == expense_id))
        await db.commit()

    @router.get("/stats", summary="Expense statistics")
    async def expense_stats(db: AsyncSession = Depends(get_db)):
        total_expense = (await db.execute(select(func.sum(Expense.amount)))).scalar() or 0
        
        # Expenses by category
        category_stats = await db.execute(
            select(Expense.category, func.sum(Expense.amount))
            .group_by(Expense.category)
        )
        by_category = {c: float(s) for c, s in category_stats.all()}
        
        # We can also try to fetch total revenue from billing plugin if it exists
        # But for now, let's keep it simple and just return expense stats
        return {
            "total_expense": round(total_expense, 2),
            "by_category": by_category,
            "count": (await db.execute(select(func.count(Expense.id)))).scalar()
        }

    app.include_router(router)
