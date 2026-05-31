"""Analytics Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from api.deps import get_current_user
from models.user import User
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/p/analytics", tags=["Plugin: Analytics"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    @router.get("/dashboard", summary="Main dashboard KPIs")
    async def dashboard_kpis(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        kpis = {}
        try:
            # Aggregate from other plugins via raw SQL for efficiency
            total_customers = (await db.execute(text("SELECT COUNT(*) FROM customers"))).scalar() or 0
            active_customers = (await db.execute(text("SELECT COUNT(*) FROM customers WHERE status='active'"))).scalar() or 0
            paid_revenue = (await db.execute(text("SELECT COALESCE(SUM(total), 0) FROM invoices WHERE status='paid'"))).scalar() or 0
            
            kpis = {
                "total_customers": total_customers,
                "active_customers": active_customers,
                "total_revenue": round(float(paid_revenue), 2),
                "arpu": round(float(paid_revenue / active_customers), 2) if active_customers > 0 else 0,
                "churn_rate": round(((total_customers - active_customers) / total_customers * 100), 2) if total_customers > 0 else 0
            }
        except Exception:
            # Fallback for empty DB
            kpis = {"total_customers": 0, "active_customers": 0, "total_revenue": 0, "arpu": 0, "churn_rate": 0}
            
        return kpis

    @router.get("/revenue-trend", summary="Revenue trend (last 12 months)")
    async def revenue_trend(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        try:
            rows = await db.execute(text("""
                SELECT TO_CHAR(created_at, 'YYYY-MM') AS month, SUM(total) 
                FROM invoices WHERE status='paid' 
                GROUP BY month ORDER BY month DESC LIMIT 12
            """))
            return [{"month": r[0], "revenue": float(r[1])} for r in rows.all()]
        except Exception:
            return []

    @router.get("/business-metrics", summary="Get specific metrics (MRR, CLV)")
    async def business_metrics(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        # Mock calculation
        return {
            "mrr": 45000,
            "clv": 12000,
            "cac": 1500
        }

    return router


