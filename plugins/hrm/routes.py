"""HRM Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from database import get_db as _get_db
from datetime import datetime

router = APIRouter(prefix="/api/p/hrm", tags=["Plugin: Hrm"])

# Models will be injected via get_router
models = {}

def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models
    
    Employee = models["Employee"]
    Department = models["Department"]
    Designation = models["Designation"]
    Attendance = models["Attendance"]
    Leave = models["Leave"]
    Salary = models["Salary"]

    # ── Employee Endpoints ────────────────────────────────────
    @router.get("/employees", summary="List all employees")
    async def list_employees(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(
            select(Employee).options(selectinload(Employee.department), selectinload(Employee.designation))
        )
        return result.scalars().all()

    @router.post("/employees", status_code=201)
    async def create_employee(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        from .models import EmployeeStatus
        if "status" in body and isinstance(body["status"], str):
            body["status"] = EmployeeStatus(body["status"])
            
        employee = Employee(**body)
        db.add(employee)
        await db.commit()
        await db.refresh(employee)
        return employee

    # ── Attendance Endpoints ──────────────────────────────────
    @router.get("/attendance", summary="List attendance")
    async def list_attendance(date: Optional[str] = None, db: AsyncSession = Depends(_get_db)):
        query = select(Attendance).options(selectinload(Attendance.employee))
        if date:
            query = query.where(Attendance.date == datetime.fromisoformat(date).date())
        result = await db.execute(query)
        return result.scalars().all()

    @router.post("/attendance/check-in", status_code=201)
    async def check_in(employee_id: int, db: AsyncSession = Depends(_get_db)):
        today = datetime.utcnow().date()
        # Check if already checked in
        result = await db.execute(
            select(Attendance).where(Attendance.employee_id == employee_id, Attendance.date == today)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(400, "Already checked in for today")
            
        attendance = Attendance(employee_id=employee_id, date=today, check_in=datetime.utcnow(), status="present")
        db.add(attendance)
        await db.commit()
        await db.refresh(attendance)
        return attendance

    # ── Leave Endpoints ───────────────────────────────────────
    @router.get("/leaves", summary="List leave applications")
    async def list_leaves(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Leave))
        return result.scalars().all()

    @router.post("/leaves", status_code=201)
    async def apply_leave(body: Dict[str, Any], db: AsyncSession = Depends(_get_db)):
        from .models import LeaveStatus
        leave = Leave(**body)
        db.add(leave)
        await db.commit()
        await db.refresh(leave)
        return leave

    # ── Salary/Payroll Endpoints ──────────────────────────────
    @router.get("/salaries", summary="List salary payments")
    async def list_salaries(db: AsyncSession = Depends(_get_db)):
        result = await db.execute(select(Salary))
        return result.scalars().all()

    @router.post("/salaries/generate", status_code=201)
    async def generate_salary(employee_id: int, month: int, year: int, db: AsyncSession = Depends(_get_db)):
        # Mock logic to generate salary from basic
        result = await db.execute(select(Employee).where(Employee.id == employee_id))
        emp = result.scalar_one_or_none()
        if not emp:
            raise HTTPException(404, "Employee not found")
            
        salary = Salary(employee_id=employee_id, month=month, year=year, amount_paid=emp.salary_basic)
        db.add(salary)
        await db.commit()
        await db.refresh(salary)
        return salary

    return router


