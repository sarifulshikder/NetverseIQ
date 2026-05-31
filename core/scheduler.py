import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import AsyncSessionLocal
from sqlalchemy import select, update
from plugins.subscription.models import Subscription, SubscriptionStatus
from plugins.billing.models import Invoice, InvoiceStatus

logger = logging.getLogger(__name__)

async def auto_suspend_expired():
    logger.info("Scheduler: Checking for expired subscriptions...")
    async with AsyncSessionLocal() as db:
        # Simplified: find subscriptions where end_date < now
        result = await db.execute(
            select(Subscription).where(Subscription.status == SubscriptionStatus.active, Subscription.end_date < datetime.utcnow())
        )
        subscriptions = result.scalars().all()
        for sub in subscriptions:
            sub.status = SubscriptionStatus.suspended
            logger.info(f"Subscription {sub.id} suspended due to expiration.")
        await db.commit()

async def check_overdue():
    logger.info("Scheduler: Checking for overdue invoices...")
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Invoice).where(Invoice.status == InvoiceStatus.unpaid, Invoice.due_date < datetime.utcnow())
        )
        invoices = result.scalars().all()
        for inv in invoices:
            inv.status = InvoiceStatus.overdue
        await db.commit()

def setup_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(auto_suspend_expired, 'cron', hour=0) # Daily at midnight
    scheduler.add_job(check_overdue, 'cron', hour=1)      # Daily at 1 AM
    return scheduler
