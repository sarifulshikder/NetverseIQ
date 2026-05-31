import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import AsyncSessionLocal
from sqlalchemy import text

logger = logging.getLogger(__name__)

async def auto_suspend_expired():
    logger.info("Scheduler: Checking for expired subscriptions...")
    async with AsyncSessionLocal() as db:
        await db.execute(text(
            "UPDATE subscriptions SET status='suspended' "
            "WHERE status='active' AND end_date < NOW()"
        ))
        await db.commit()

async def check_overdue():
    logger.info("Scheduler: Checking for overdue invoices...")
    async with AsyncSessionLocal() as db:
        await db.execute(text(
            "UPDATE invoices SET status='overdue' "
            "WHERE status='unpaid' AND due_date < NOW()"
        ))
        await db.commit()

def setup_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(auto_suspend_expired, 'cron', hour=0) # Daily at midnight
    scheduler.add_job(check_overdue, 'cron', hour=1)      # Daily at 1 AM
    return scheduler
