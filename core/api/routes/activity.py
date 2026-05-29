"""
NetverseIQ — Activity Log Routes
GET /api/activity        → list logs (superuser only)
GET /api/activity/mine   → current user's own logs
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from datetime import datetime

from database import get_db
from api.deps import get_current_user, require_superuser
from models.user import User
from models.activity_log import ActivityLog

router = APIRouter()


def _clean(log) -> dict:
    return {
        "id": log.id,
        "user_id": log.user_id,
        "action": log.action,
        "resource": log.resource,
        "detail": log.detail,
        "ip_address": log.ip_address,
        "meta": log.meta,
        "created_at": log.created_at.isoformat(),
    }


@router.get("/", summary="List all activity logs (superuser)")
async def list_logs(
    skip: int = 0,
    limit: int = 100,
    action: str = "",
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_superuser),
):
    q = select(ActivityLog).order_by(desc(ActivityLog.created_at))
    if action:
        q = q.where(ActivityLog.action.ilike(f"%{action}%"))
    result = await db.execute(q.offset(skip).limit(limit))
    logs = result.scalars().all()
    return {"total": len(logs), "items": [_clean(l) for l in logs]}


@router.get("/mine", summary="Current user's activity")
async def my_logs(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(ActivityLog).where(
        ActivityLog.user_id == current_user.id
    ).order_by(desc(ActivityLog.created_at))
    result = await db.execute(q.offset(skip).limit(limit))
    logs = result.scalars().all()
    return {"total": len(logs), "items": [_clean(l) for l in logs]}
