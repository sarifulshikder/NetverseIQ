"""Area Zone Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


def register_models(Base):
    """Register Area & Zone models with the shared SQLAlchemy Base."""

    class Area(Base):
        __tablename__ = "areas"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), index=True)
        parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("areas.id"), nullable=True)
        description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        
        children = relationship("Area", backref="parent", remote_side=[id])
        zones = relationship("Zone", back_populates="area")

    class Zone(Base):
        __tablename__ = "zones"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), index=True)
        area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"))
        
        # Google Maps polygon or coordinates
        polygon_coordinates: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
        
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        area = relationship("Area", back_populates="zones")
        assignments = relationship("ZoneAssignment", back_populates="zone")

    class ZoneAssignment(Base):
        __tablename__ = "zone_assignments"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"))
        technician_id: Mapped[int] = mapped_column(Integer) # Linked to employees.id (HRM)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        zone = relationship("Zone", back_populates="assignments")

    return {
        "Area": Area,
        "Zone": Zone,
        "ZoneAssignment": ZoneAssignment
    }
