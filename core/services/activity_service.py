"""
NetverseIQ — Activity Log Service
Every important action calls log_activity() to record audit trail.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from models.activity_log import ActivityLog


async def log_activity(
    db: AsyncSession,
    action: str,
    user_id: int = None,
    resource: str = "",
    detail: str = "",
    ip_address: str = "",
    meta: dict = None,
) -> None:
    """
    Record an audit log entry.
    action   : dot-notation e.g. "customer.create", "invoice.paid"
    resource : e.g. "customer:42", "invoice:INV-202405-001"
    """
    log = ActivityLog(
        user_id=user_id,
        action=action,
        resource=resource,
        detail=detail,
        ip_address=ip_address,
        meta=meta or {},
    )
    db.add(log)
    # No commit here — caller commits
