"""
NetverseIQ Plugin: Analytics & Reports
Aggregates data from other plugins to provide KPIs and trends.
"""
from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from datetime import datetime, timedelta


def register(app: FastAPI, Base) -> None:
    from database import get_db

    router = APIRouter(prefix="/api/p/analytics", tags=["Plugin: Analytics"])

    @router.get("/dashboard", summary="Main dashboard KPIs")
    async def dashboard_kpis(db: AsyncSession = Depends(get_db)):
        """Aggregate KPIs from customers and billing tables (if available)."""
        kpis = {}

        # Customer stats
        try:
            total_customers = (await db.execute(text("SELECT COUNT(*) FROM customers"))).scalar() or 0
            active_customers = (await db.execute(text("SELECT COUNT(*) FROM customers WHERE status='active'"))).scalar() or 0
            kpis["total_customers"] = total_customers
            kpis["active_customers"] = active_customers
            kpis["churn_rate"] = round(
                ((total_customers - active_customers) / total_customers * 100) if total_customers > 0 else 0, 1
            )
        except Exception:
            kpis["total_customers"] = 0
            kpis["active_customers"] = 0
            kpis["churn_rate"] = 0

        # Billing stats
        try:
            total_revenue = (await db.execute(
                text("SELECT COALESCE(SUM(total), 0) FROM invoices WHERE status='paid'")
            )).scalar() or 0
            pending_dues = (await db.execute(
                text("SELECT COALESCE(SUM(total), 0) FROM invoices WHERE status='unpaid'")
            )).scalar() or 0
            kpis["total_revenue"] = round(float(total_revenue), 2)
            kpis["pending_dues"] = round(float(pending_dues), 2)
        except Exception:
            kpis["total_revenue"] = 0
            kpis["pending_dues"] = 0

        # Notification stats
        try:
            notif_sent = (await db.execute(
                text("SELECT COUNT(*) FROM notifications WHERE status='sent'")
            )).scalar() or 0
            kpis["notifications_sent"] = notif_sent
        except Exception:
            kpis["notifications_sent"] = 0

        return kpis

    @router.get("/revenue-trend", summary="Monthly revenue for last 6 months")
    async def revenue_trend(db: AsyncSession = Depends(get_db)):
        """Returns month-by-month revenue for the past 6 months."""
        try:
            rows = await db.execute(text("""
                SELECT
                    TO_CHAR(created_at, 'YYYY-MM') AS month,
                    COALESCE(SUM(total), 0) AS revenue
                FROM invoices
                WHERE status = 'paid'
                  AND created_at >= NOW() - INTERVAL '6 months'
                GROUP BY month
                ORDER BY month
            """))
            return [{"month": r[0], "revenue": round(float(r[1]), 2)} for r in rows]
        except Exception:
            return []

    @router.get("/customer-growth", summary="New customers per month (last 6 months)")
    async def customer_growth(db: AsyncSession = Depends(get_db)):
        try:
            rows = await db.execute(text("""
                SELECT
                    TO_CHAR(created_at, 'YYYY-MM') AS month,
                    COUNT(*) AS new_customers
                FROM customers
                WHERE created_at >= NOW() - INTERVAL '6 months'
                GROUP BY month
                ORDER BY month
            """))
            return [{"month": r[0], "new_customers": r[1]} for r in rows]
        except Exception:
            return []

    app.include_router(router)
