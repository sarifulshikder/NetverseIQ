"""Expense Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
import enum


class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


def register_models(Base):
    """Register Expense models with the shared SQLAlchemy Base."""

    class ExpenseCategory(Base):
        __tablename__ = "expense_categories"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), unique=True)
        description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        
        expenses = relationship("Expense", back_populates="category")

    class Expense(Base):
        __tablename__ = "expenses"
        __table_args__ = {"extend_existing": True}

        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        title: Mapped[str] = mapped_column(String(256), index=True)
        category_id: Mapped[int] = mapped_column(ForeignKey("expense_categories.id"))
        
        amount: Mapped[float] = mapped_column(Float, default=0.0)
        date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        payment_method: Mapped[str] = mapped_column(String(64), default="Cash")
        reference: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
        receipt_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
        
        is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
        approval_status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.approved)
        
        description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        category = relationship("ExpenseCategory", back_populates="expenses")

    class Budget(Base):
        __tablename__ = "budgets"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        category_id: Mapped[int] = mapped_column(ForeignKey("expense_categories.id"))
        amount: Mapped[float] = mapped_column(Float)
        period: Mapped[str] = mapped_column(String(32), default="monthly") # monthly, yearly
        year: Mapped[int] = mapped_column(Integer)
        month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class ExpenseApproval(Base):
        __tablename__ = "expense_approvals"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        expense_id: Mapped[int] = mapped_column(ForeignKey("expenses.id"))
        approver_id: Mapped[int] = mapped_column(Integer) # Staff ID
        status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus))
        comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    return {
        "ExpenseCategory": ExpenseCategory,
        "Expense": Expense,
        "Budget": Budget,
        "ExpenseApproval": ExpenseApproval
    }
