"""
NetverseIQ Plugin: Support & Ticketing
Manages customer support tickets.
"""
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from datetime import datetime
from typing import List, Optional
import enum

def register(app: FastAPI, Base) -> None:

    # ── Models ────────────────────────────────────────────────
    from sqlalchemy import Integer, String, Text, DateTime, Enum as SQLEnum
    from sqlalchemy.orm import Mapped, mapped_column

    class TicketStatus(str, enum.Enum):
        open = "open"
        in_progress = "in_progress"
        resolved = "resolved"
        closed = "closed"

    class TicketPriority(str, enum.Enum):
        low = "low"
        medium = "medium"
        high = "high"
        urgent = "urgent"

    class Ticket(Base):
        __tablename__ = "support_tickets"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        customer_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
        customer_name: Mapped[str] = mapped_column(String(256), default="")
        subject: Mapped[str] = mapped_column(String(256), nullable=False)
        description: Mapped[str] = mapped_column(Text, nullable=False)
        status: Mapped[TicketStatus] = mapped_column(SQLEnum(TicketStatus), default=TicketStatus.open)
        priority: Mapped[TicketPriority] = mapped_column(SQLEnum(TicketPriority), default=TicketPriority.medium)
        category: Mapped[str] = mapped_column(String(64), default="general") # technical, billing, general, sales
        assigned_to: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Routes ────────────────────────────────────────────────
    from database import get_db

    router = APIRouter(prefix="/api/p/support", tags=["Plugin: Support"])

    def _clean(obj):
        if not obj: return None
        d = obj.__dict__.copy()
        d.pop("_sa_instance_state", None)
        return d

    @router.get("/tickets", summary="List support tickets")
    async def list_tickets(
        skip: int = 0, limit: int = 50, 
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        customer_id: Optional[int] = None,
        db: AsyncSession = Depends(get_db),
    ):
        q = select(Ticket)
        if status:
            q = q.where(Ticket.status == status)
        if priority:
            q = q.where(Ticket.priority == priority)
        if customer_id:
            q = q.where(Ticket.customer_id == customer_id)
        
        q = q.order_by(Ticket.created_at.desc())
        
        result = await db.execute(q.offset(skip).limit(limit))
        items = [_clean(r) for r in result.scalars().all()]
        
        count_q = select(func.count(Ticket.id))
        if status: count_q = count_q.where(Ticket.status == status)
        if priority: count_q = count_q.where(Ticket.priority == priority)
        if customer_id: count_q = count_q.where(Ticket.customer_id == customer_id)
        
        total = (await db.execute(count_q)).scalar()
        
        return {"total": total, "items": items}

    @router.post("/tickets", status_code=201, summary="Create a support ticket")
    async def create_ticket(body: dict, db: AsyncSession = Depends(get_db)):
        # Basic validation
        if not body.get("customer_id") or not body.get("subject") or not body.get("description"):
            raise HTTPException(400, "customer_id, subject, and description are required")
        
        ticket = Ticket(**body)
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        return _clean(ticket)

    @router.get("/tickets/{ticket_id}", summary="Get ticket details")
    async def get_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalar_one_or_none()
        if not ticket:
            raise HTTPException(404, "Ticket not found")
        return _clean(ticket)

    @router.put("/tickets/{ticket_id}", summary="Update a ticket")
    async def update_ticket(ticket_id: int, body: dict, db: AsyncSession = Depends(get_db)):
        # Remove protected fields
        body.pop("id", None)
        body.pop("created_at", None)
        body.pop("updated_at", None)
        
        if not body:
            raise HTTPException(400, "No fields to update")

        await db.execute(
            update(Ticket).where(Ticket.id == ticket_id).values(**body)
        )
        await db.commit()
        
        result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
        return _clean(result.scalar_one_or_none())

    @router.get("/stats", summary="Support statistics")
    async def support_stats(db: AsyncSession = Depends(get_db)):
        total = (await db.execute(select(func.count(Ticket.id)))).scalar()
        open_count = (await db.execute(select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.open))).scalar()
        in_progress = (await db.execute(select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.in_progress))).scalar()
        resolved = (await db.execute(select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.resolved))).scalar()
        urgent = (await db.execute(select(func.count(Ticket.id)).where(Ticket.priority == TicketPriority.urgent))).scalar()
        
        return {
            "total_tickets": total,
            "open_tickets": open_count,
            "in_progress": in_progress,
            "resolved": resolved,
            "urgent_tickets": urgent
        }

    app.include_router(router)
