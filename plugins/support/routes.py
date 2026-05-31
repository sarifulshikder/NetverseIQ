"""Support Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from datetime import datetime, timedelta
import random
import string

router = APIRouter(prefix="/api/p/support", tags=["Plugin: Support"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    Ticket = models["Ticket"]
    TicketReply = models["TicketReply"]
    TicketCategory = models["TicketCategory"]
    FieldVisit = models["FieldVisit"]

    def gen_ticket_no():
        suffix = ''.join(random.choices(string.digits, k=6))
        return f"TKT-{datetime.utcnow().strftime('%Y%m')}-{suffix}"

    # ── Ticket Endpoints ──────────────────────────────────────
    @router.get("/", summary="List all tickets")
    async def list_tickets(
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        customer_id: Optional[int] = None,
        db: AsyncSession = Depends(_get_db),
    ):
        query = select(Ticket)
        if status:
            query = query.where(Ticket.status == status)
        if priority:
            query = query.where(Ticket.priority == priority)
        if customer_id:
            query = query.where(Ticket.customer_id == customer_id)
            
        result = await db.execute(query.offset(skip).limit(limit).order_by(Ticket.created_at.desc()))
        items = result.scalars().all()
        total = (await db.execute(select(func.count(Ticket.id)))).scalar()
        return {"total": total, "items": items}

    @router.post("/", status_code=status.HTTP_201_CREATED, summary="Create ticket")
    async def create_ticket(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        if not body.get("ticket_no"):
            body["ticket_no"] = gen_ticket_no()
            
        # Handle enums
        from .models import TicketStatus, TicketPriority
        if "status" in body and isinstance(body["status"], str):
            body["status"] = TicketStatus(body["status"])
        if "priority" in body and isinstance(body["priority"], str):
            body["priority"] = TicketPriority(body["priority"])

        # SLA Calculation (Mock logic)
        category_id = body.get("category_id")
        if category_id:
            cat_result = await db.execute(select(TicketCategory).where(TicketCategory.id == category_id))
            cat = cat_result.scalar_one_or_none()
            if cat:
                body["sla_deadline"] = datetime.utcnow() + timedelta(hours=cat.sla_hours)

        ticket = Ticket(**body)
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        return ticket

    @router.get("/stats", summary="Support statistics")
    async def support_stats(db: AsyncSession = Depends(_get_db)):
        total = (await db.execute(select(func.count(Ticket.id)))).scalar()
        open_count = (await db.execute(select(func.count(Ticket.id)).where(Ticket.status == "open"))).scalar()
        resolved = (await db.execute(select(func.count(Ticket.id)).where(Ticket.status == "resolved"))).scalar()
        breached = (await db.execute(select(func.count(Ticket.id)).where(Ticket.is_sla_breached == True))).scalar()
        
        return {
            "total_tickets": total,
            "open_tickets": open_count,
            "resolved": resolved,
            "sla_breached": breached,
            "resolution_rate": round((resolved / total * 100), 2) if total > 0 else 0
        }

    @router.get("/{ticket_id}", summary="Get ticket by ID")
    async def get_ticket(ticket_id: int, db: AsyncSession = Depends(_get_db)):
        result = await db.execute(
            select(Ticket)
            .where(Ticket.id == ticket_id)
            .options(selectinload(Ticket.replies), selectinload(Ticket.visits))
        )
        ticket = result.scalar_one_or_none()
        if not ticket:
            raise HTTPException(404, "Ticket not found")
        return ticket

    @router.post("/{ticket_id}/replies", status_code=201)
    async def add_reply(ticket_id: int, body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        reply = TicketReply(ticket_id=ticket_id, **body)
        db.add(reply)
        
        # Update ticket timestamp
        await db.execute(update(Ticket).where(Ticket.id == ticket_id).values(updated_at=datetime.utcnow()))
        
        await db.commit()
        await db.refresh(reply)
        return reply

    @router.post("/{ticket_id}/visits", status_code=201)
    async def schedule_visit(ticket_id: int, body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        visit = FieldVisit(ticket_id=ticket_id, **body)
        db.add(visit)
        
        # Update ticket status to in_progress
        from .models import TicketStatus
        await db.execute(update(Ticket).where(Ticket.id == ticket_id).values(status=TicketStatus.in_progress))
        
        await db.commit()
        await db.refresh(visit)
        return visit

    return router


