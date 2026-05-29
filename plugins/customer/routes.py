"""Customer Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

router = APIRouter()

# Models registered lazily (set by plugin.py after Base is ready)
Customer = None


def get_router(customer_model):
    global Customer
    Customer = customer_model

    @router.get("/", summary="List all customers")
    async def list_customers(
        skip: int = 0,
        limit: int = 50,
        search: str = "",
        db: AsyncSession = Depends(_get_db),
    ):
        query = select(Customer)
        if search:
            query = query.where(
                Customer.name.ilike(f"%{search}%") |
                Customer.email.ilike(f"%{search}%") |
                Customer.connection_id.ilike(f"%{search}%")
            )
        result = await db.execute(query.offset(skip).limit(limit))
        customers = result.scalars().all()
        count_result = await db.execute(select(func.count(Customer.id)))
        total = count_result.scalar()
        return {"total": total, "items": customers}

    @router.post("/", status_code=status.HTTP_201_CREATED, summary="Create customer")
    async def create_customer(body: dict, db: AsyncSession = Depends(_get_db)):
        customer = Customer(**body)
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer

    @router.get("/stats", summary="Customer statistics")
    async def customer_stats(db: AsyncSession = Depends(_get_db)):
        total = (await db.execute(select(func.count(Customer.id)))).scalar()
        active = (await db.execute(
            select(func.count(Customer.id)).where(Customer.status == "active")
        )).scalar()
        suspended = (await db.execute(
            select(func.count(Customer.id)).where(Customer.status == "suspended")
        )).scalar()
        pending = (await db.execute(
            select(func.count(Customer.id)).where(Customer.status == "pending")
        )).scalar()
        return {
            "total": total,
            "active": active,
            "suspended": suspended,
            "pending": pending,
            "expired": total - active - suspended - pending,
        }

    @router.get("/{customer_id}", summary="Get customer by ID")
    async def get_customer(customer_id: int, db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        c = result.scalar_one_or_none()
        if not c:
            raise HTTPException(status_code=404, detail="Customer not found")
        return c

    @router.put("/{customer_id}", summary="Update customer")
    async def update_customer(customer_id: int, body: dict, db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        c = result.scalar_one_or_none()
        if not c:
            raise HTTPException(status_code=404, detail="Customer not found")
        for k, v in body.items():
            if hasattr(c, k) and v is not None:
                setattr(c, k, v)
        await db.commit()
        await db.refresh(c)
        return c

    @router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_customer(customer_id: int, db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        c = result.scalar_one_or_none()
        if not c:
            raise HTTPException(status_code=404, detail="Customer not found")
        await db.delete(c)
        await db.commit()

    return router


def _get_db():
    """Import lazily to avoid circular imports at module load time."""
    from database import get_db
    return Depends(get_db)
