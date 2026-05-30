"""Expense Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/p/expense", tags=["Plugin: Expense"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    Expense = models["Expense"]
    ExpenseCategory = models["ExpenseCategory"]
    Budget = models["Budget"]
    ExpenseApproval = models["ExpenseApproval"]

    # ── Expense Endpoints ─────────────────────────────────────
    @router.get("/", summary="List all expenses")
    async def list_expenses(
        skip: int = 0,
        limit: int = 50,
        category_id: Optional[int] = None,
        db: AsyncSession = Depends(_get_db),
    ):
        query = select(Expense).options(selectinload(Expense.category))
        if category_id:
            query = query.where(Expense.category_id == category_id)
        result = await db.execute(query.offset(skip).limit(limit).order_by(Expense.date.desc()))
        return result.scalars().all()

    @router.post("/", status_code=status.HTTP_201_CREATED)
    async def create_expense(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        from .models import ApprovalStatus
        if "approval_status" in body and isinstance(body["approval_status"], str):
            body["approval_status"] = ApprovalStatus(body["approval_status"])
            
        expense = Expense(**body)
        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        return expense

    @router.get("/stats", summary="Expense statistics")
    async def expense_stats(db: AsyncSession = Depends(_get_db)):
        total = (await db.execute(select(func.sum(Expense.amount)))).scalar() or 0
        
        # Breakdown by category
        cat_stats_query = select(ExpenseCategory.name, func.sum(Expense.amount)).join(Expense).group_by(ExpenseCategory.name)
        cat_stats = (await db.execute(cat_stats_query)).all()
        
        return {
            "total_expense": round(total, 2),
            "category_breakdown": {cat: round(amount, 2) for cat, amount in cat_stats}
        }

    # ── Category Endpoints ────────────────────────────────────
    @router.get("/categories", summary="List expense categories")
    async def list_categories(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(ExpenseCategory))
        return result.scalars().all()

    @router.post("/categories", status_code=201)
    async def create_category(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        cat = ExpenseCategory(**body)
        db.add(cat)
        await db.commit()
        await db.refresh(cat)
        return cat

    # ── Budget Endpoints ──────────────────────────────────────
    @router.get("/budgets", summary="List budgets")
    async def list_budgets(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Budget))
        return result.scalars().all()

    @router.post("/budgets", status_code=201)
    async def create_budget(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        budget = Budget(**body)
        db.add(budget)
        await db.commit()
        await db.refresh(budget)
        return budget

    return router


def _get_db():
    from database import get_db
    return Depends(get_db)
