"""Customer Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from api.deps import get_current_user
from models.user import User
from datetime import datetime
import os
import shutil

router = APIRouter(prefix="/api/p/customer", tags=["Plugin: Customer"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    Customer = models["Customer"]
    CustomerDocument = models["CustomerDocument"]
    CustomerAddress = models["CustomerAddress"]
    CustomerContact = models["CustomerContact"]
    CustomerNote = models["CustomerNote"]

    @router.get("/", summary="List all customers")
    async def list_customers(
        skip: int = 0,
        limit: int = 50,
        search: str = "",
        status: Optional[str] = None,
        customer_type: Optional[str] = None,
        area_zone: Optional[str] = None,
        db: AsyncSession = Depends(_get_db),
     current_user: User = Depends(get_current_user),):
        query = select(Customer)
        
        # Filters
        if search:
            query = query.where(
                or_(
                    Customer.name.ilike(f"%{search}%"),
                    Customer.email.ilike(f"%{search}%"),
                    Customer.connection_id.ilike(f"%{search}%"),
                    Customer.customer_id.ilike(f"%{search}%"),
                    Customer.phone.ilike(f"%{search}%")
                )
            )
        if status:
            query = query.where(Customer.status == status)
        if customer_type:
            query = query.where(Customer.customer_type == customer_type)
        if area_zone:
            query = query.where(Customer.area_zone == area_zone)
            
        result = await db.execute(query.offset(skip).limit(limit))
        items = result.scalars().all()
        
        count_query = select(func.count(Customer.id))
        if search: # Apply same filters for count
             count_query = count_query.where(
                or_(
                    Customer.name.ilike(f"%{search}%"),
                    Customer.email.ilike(f"%{search}%"),
                    Customer.connection_id.ilike(f"%{search}%"),
                    Customer.customer_id.ilike(f"%{search}%"),
                    Customer.phone.ilike(f"%{search}%")
                )
            )
        if status: count_query = count_query.where(Customer.status == status)
        
        total = (await db.execute(count_query)).scalar()
        
        return {"total": total, "items": items}

    @router.post("/", status_code=status.HTTP_201_CREATED, summary="Create customer")
    async def create_customer(body: Dict[str, Any], db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        # Auto-generate customer_id
        current_year = datetime.now().year
        prefix = f"CUS-{current_year}-"
        
        # Find last customer ID for this year
        last_customer_query = select(Customer).where(Customer.customer_id.like(f"{prefix}%")).order_by(Customer.customer_id.desc()).limit(1)
        last_customer = (await db.execute(last_customer_query)).scalar_one_or_none()
        
        if last_customer and last_customer.customer_id:
            last_serial = int(last_customer.customer_id.split("-")[-1])
            new_serial = last_serial + 1
        else:
            new_serial = 1
            
        body["customer_id"] = f"{prefix}{new_serial:04d}"
        
        # Handle status as enum if string provided
        from .models import CustomerStatus, CustomerType
        if "status" in body and isinstance(body["status"], str):
            body["status"] = CustomerStatus(body["status"])
        if "customer_type" in body and isinstance(body["customer_type"], str):
            body["customer_type"] = CustomerType(body["customer_type"])

        customer = Customer(**body)
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        
        # Log activity
        from core.services.activity_service import log_activity
        await log_activity(db, "customer.create", resource=f"customer:{customer.id}", detail=f"Created customer {customer.name}")
        await db.commit()
        
        return customer

    @router.get("/stats", summary="Customer statistics")
    async def customer_stats(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        total = (await db.execute(select(func.count(Customer.id)))).scalar()
        active = (await db.execute(select(func.count(Customer.id)).where(Customer.status == "active"))).scalar()
        suspended = (await db.execute(select(func.count(Customer.id)).where(Customer.status == "suspended"))).scalar()
        pending = (await db.execute(select(func.count(Customer.id)).where(Customer.status == "pending"))).scalar()
        
        # Area-wise breakdown
        area_stats_query = select(Customer.area_zone, func.count(Customer.id)).group_by(Customer.area_zone)
        area_stats = (await db.execute(area_stats_query)).all()
        
        return {
            "total": total,
            "active": active,
            "suspended": suspended,
            "pending": pending,
            "expired": total - active - suspended - pending,
            "area_breakdown": {area: count for area, count in area_stats}
        }

    @router.get("/{customer_id}", summary="Get customer by ID")
    async def get_customer(customer_id: int, db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(
            select(Customer)
            .where(Customer.id == customer_id)
        )
        c = result.scalar_one_or_none()
        if not c:
            raise HTTPException(status_code=404, detail="Customer not found")
        return c

    @router.get("/{customer_id}/timeline", summary="Customer timeline")
    async def get_customer_timeline(customer_id: int, db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        from core.models.activity_log import ActivityLog
        result = await db.execute(
            select(ActivityLog)
            .where(ActivityLog.resource == f"customer:{customer_id}")
            .order_by(ActivityLog.created_at.desc())
        )
        return result.scalars().all()

    @router.get("/{customer_id}/documents", summary="Get customer documents")
    async def get_customer_documents(customer_id: int, db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(CustomerDocument).where(CustomerDocument.customer_id == customer_id))
        return result.scalars().all()

    @router.post("/{customer_id}/documents", summary="Upload customer document")
    async def upload_document(
        customer_id: int, 
        doc_type: str, 
        file: UploadFile = File(...), 
        expiry_date: Optional[str] = None,
        db: AsyncSession = Depends(_get_db)
    , current_user: User = Depends(get_current_user)):
        # Save file logic (minimal)
        upload_dir = f"uploads/customers/{customer_id}/docs"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        expiry = None
        if expiry_date:
            expiry = datetime.fromisoformat(expiry_date)
            
        doc = CustomerDocument(
            customer_id=customer_id,
            doc_type=doc_type,
            file_path=file_path,
            expiry_date=expiry
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc

    @router.put("/{customer_id}", summary="Update customer")
    async def update_customer(customer_id: int, body: Dict[str, Any], db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        c = result.scalar_one_or_none()
        if not c:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        for k, v in body.items():
            if hasattr(c, k) and k not in ("id", "customer_id", "created_at"):
                if k == "status" and isinstance(v, str):
                    from .models import CustomerStatus
                    v = CustomerStatus(v)
                if k == "customer_type" and isinstance(v, str):
                    from .models import CustomerType
                    v = CustomerType(v)
                setattr(c, k, v)
        
        await db.commit()
        await db.refresh(c)
        return c

    @router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_customer(customer_id: int, db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        c = result.scalar_one_or_none()
        if not c:
            raise HTTPException(status_code=404, detail="Customer not found")
        await db.delete(c)
        await db.commit()

    return router


