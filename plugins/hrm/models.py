"""HRM Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Enum, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
import enum


class EmployeeStatus(str, enum.Enum):
    active = "active"
    on_leave = "on_leave"
    terminated = "terminated"


class LeaveStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


def register_models(Base):
    """Register HRM models with the shared SQLAlchemy Base."""

    class Department(Base):
        __tablename__ = "departments"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), unique=True)
        description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        
        employees = relationship("Employee", back_populates="department")

    class Designation(Base):
        __tablename__ = "designations"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), unique=True)
        
        employees = relationship("Employee", back_populates="designation")

    class Employee(Base):
        __tablename__ = "employees"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(256), index=True)
        email: Mapped[str] = mapped_column(String(256), unique=True, index=True)
        phone: Mapped[str] = mapped_column(String(32))
        
        department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
        designation_id: Mapped[int] = mapped_column(ForeignKey("designations.id"))
        
        join_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        status: Mapped[EmployeeStatus] = mapped_column(Enum(EmployeeStatus), default=EmployeeStatus.active)
        
        salary_basic: Mapped[float] = mapped_column(Float, default=0.0)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        department = relationship("Department", back_populates="employees")
        designation = relationship("Designation", back_populates="employees")
        attendance = relationship("Attendance", back_populates="employee")

    class Attendance(Base):
        __tablename__ = "attendance"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
        date: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow)
        check_in: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
        check_out: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
        status: Mapped[str] = mapped_column(String(32), default="present") # present, absent, late, early_out
        
        employee = relationship("Employee", back_populates="attendance")

    class Leave(Base):
        __tablename__ = "leaves"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
        leave_type: Mapped[str] = mapped_column(String(64)) # casual, sick, annual
        start_date: Mapped[datetime] = mapped_column(Date)
        end_date: Mapped[datetime] = mapped_column(Date)
        status: Mapped[LeaveStatus] = mapped_column(Enum(LeaveStatus), default=LeaveStatus.pending)
        reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    class Salary(Base):
        __tablename__ = "salaries"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
        month: Mapped[int] = mapped_column(Integer)
        year: Mapped[int] = mapped_column(Integer)
        amount_paid: Mapped[float] = mapped_column(Float)
        paid_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    return {
        "Department": Department,
        "Designation": Designation,
        "Employee": Employee,
        "Attendance": Attendance,
        "Leave": Leave,
        "Salary": Salary
    }
