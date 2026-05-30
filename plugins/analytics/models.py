"""Analytics Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from typing import List, Optional


def register_models(Base):
    """Register Analytics models (if any) with the shared SQLAlchemy Base."""

    class BusinessMetric(Base):
        __tablename__ = "business_metrics"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        metric_name: Mapped[str] = mapped_column(String(128), index=True) # ARPU, MRR, Churn
        metric_value: Mapped[float] = mapped_column(Float)
        period_start: Mapped[datetime] = mapped_column(DateTime)
        period_end: Mapped[datetime] = mapped_column(DateTime)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    return {
        "BusinessMetric": BusinessMetric
    }
