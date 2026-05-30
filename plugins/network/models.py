"""Network Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, ForeignKey, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


def register_models(Base):
    """Register Network models with the shared SQLAlchemy Base."""

    class NASDevice(Base):
        __tablename__ = "nas_devices"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), index=True)
        ip_address: Mapped[str] = mapped_column(String(45), unique=True, index=True)
        device_type: Mapped[str] = mapped_column(String(64)) # MikroTik, Cisco, etc.
        secret: Mapped[str] = mapped_column(String(256)) # RADIUS secret
        vendor: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
        
        # Connection details
        api_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        username: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
        password: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        ip_assignments = relationship("IPAssignment", back_populates="nas")

    class NetworkNode(Base):
        __tablename__ = "network_nodes"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128))
        node_type: Mapped[str] = mapped_column(String(64)) # Router, Switch, OLT, ONU
        status: Mapped[str] = mapped_column(String(32), default="online")
        ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
        area_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # Linked to areas.id
        
        meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class IPPool(Base):
        __tablename__ = "ip_pools"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), unique=True)
        start_ip: Mapped[str] = mapped_column(String(45))
        end_ip: Mapped[str] = mapped_column(String(45))
        gateway: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
        dns: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        
        assignments = relationship("IPAssignment", back_populates="pool")

    class IPAssignment(Base):
        __tablename__ = "ip_assignments"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        ip_address: Mapped[str] = mapped_column(String(45), unique=True, index=True)
        pool_id: Mapped[int] = mapped_column(ForeignKey("ip_pools.id"))
        customer_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        subscription_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        nas_id: Mapped[Optional[int]] = mapped_column(ForeignKey("nas_devices.id"), nullable=True)
        
        assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        pool = relationship("IPPool", back_populates="assignments")
        nas = relationship("NASDevice", back_populates="ip_assignments")

    class NetworkLink(Base):
        __tablename__ = "network_links"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        from_node_id: Mapped[int] = mapped_column(ForeignKey("network_nodes.id"))
        to_node_id: Mapped[int] = mapped_column(ForeignKey("network_nodes.id"))
        bandwidth_mbps: Mapped[int] = mapped_column(Integer)
        link_type: Mapped[str] = mapped_column(String(64)) # Fiber, Wireless, Cat6
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class NetworkOutage(Base):
        __tablename__ = "network_outages"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
        affected_customers_count: Mapped[int] = mapped_column(Integer, default=0)
        reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        status: Mapped[str] = mapped_column(String(32), default="active") # active, resolved

    return {
        "NASDevice": NASDevice,
        "NetworkNode": NetworkNode,
        "IPPool": IPPool,
        "IPAssignment": IPAssignment,
        "NetworkLink": NetworkLink,
        "NetworkOutage": NetworkOutage
    }
