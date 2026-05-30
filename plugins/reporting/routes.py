"""Reporting Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/p/reporting", tags=["Plugin: Reporting"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    # ── Financial Reports ─────────────────────────────────────
    @router.get("/financial/summary", summary="Aggregate financial summary")
    async def get_financial_summary(db: AsyncSession = Depends(_get_db)):
        # In a real app, we'd query billing and expense models
        return {
            "total_revenue": 500000,
            "total_expense": 200000,
            "net_profit": 300000,
            "outstanding_dues": 50000
        }

    # ── Customer Reports ──────────────────────────────────────
    @router.get("/customers/growth", summary="Customer growth over time")
    async def get_customer_growth(db: AsyncSession = Depends(_get_db)):
        return {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
            "data": [100, 150, 210, 300, 450]
        }

    # ── Support Reports ───────────────────────────────────────
    @router.get("/support/performance", summary="Support team performance")
    async def get_support_performance(db: AsyncSession = Depends(_get_db)):
        return {
            "avg_resolution_time": "4.5 hours",
            "sla_compliance": "98%",
            "tickets_by_category": {
                "technical": 45,
                "billing": 20,
                "hardware": 15
            }
        }

    # ── Export ────────────────────────────────────────────────
    @router.get("/export/{report_type}", summary="Export report to CSV/PDF")
    async def export_report(report_type: str):
        return {"status": "success", "message": f"Report {report_type} exported (mock)"}

    return router


def _get_db():
    from database import get_db
    return Depends(get_db)
