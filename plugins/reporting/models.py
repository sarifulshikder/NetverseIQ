"""Reporting Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


def register_models(Base):
    """Register Reporting models with the shared SQLAlchemy Base."""

    class ReportTemplate(Base):
        __tablename__ = "report_templates"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), unique=True)
        config: Mapped[dict] = mapped_column(JSON) # Columns, Filters, Charts
        category: Mapped[str] = mapped_column(String(64)) # finance, customer, network, support
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class ReportSchedule(Base):
        __tablename__ = "report_schedules"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        template_id: Mapped[int] = mapped_column(ForeignKey("report_templates.id"))
        frequency: Mapped[str] = mapped_column(String(32)) # daily, weekly, monthly
        recipients: Mapped[str] = mapped_column(Text) # Comma separated emails
        
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    return {
        "ReportTemplate": ReportTemplate,
        "ReportSchedule": ReportSchedule
    }
