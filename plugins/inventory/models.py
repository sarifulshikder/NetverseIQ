from decimal import Decimal
"""Inventory Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import Numeric, String, Boolean, DateTime, Text, Integer, ForeignKey, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
import enum


class StockAction(str, enum.Enum):
    stock_in = "stock_in"
    stock_out = "stock_out"
    transfer = "transfer"
    adjustment = "adjustment"


def register_models(Base):
    """Register Inventory models with the shared SQLAlchemy Base."""

    class ProductCategory(Base):
        __tablename__ = "product_categories"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), unique=True)
        description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        
        products = relationship("Product", back_populates="category")

    class Product(Base):
        __tablename__ = "products"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(256), index=True)
        brand: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
        model: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
        
        category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_categories.id"), nullable=True)
        unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
        
        min_stock_level: Mapped[int] = mapped_column(Integer, default=5)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        
        category = relationship("ProductCategory", back_populates="products")
        stock = relationship("Stock", back_populates="product")

    class Warehouse(Base):
        __tablename__ = "warehouses"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(128), unique=True)
        location: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        
        stock = relationship("Stock", back_populates="warehouse")

    class Stock(Base):
        __tablename__ = "stock"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
        warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
        quantity: Mapped[int] = mapped_column(Integer, default=0)
        
        product = relationship("Product", back_populates="stock")
        warehouse = relationship("Warehouse", back_populates="stock")

    class StockMovement(Base):
        __tablename__ = "stock_movements"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
        warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
        
        quantity: Mapped[int] = mapped_column(Integer)
        action: Mapped[StockAction] = mapped_column(Enum(StockAction))
        
        reference: Mapped[Optional[str]] = mapped_column(String(128), nullable=True) # PO number, Ticket ID
        notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class EquipmentAssignment(Base):
        __tablename__ = "equipment_assignments"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        customer_id: Mapped[int] = mapped_column(Integer, index=True)
        product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
        serial_no: Mapped[str] = mapped_column(String(128), unique=True, index=True)
        
        status: Mapped[str] = mapped_column(String(32), default="active") # active, returned, faulty
        assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    class Vendor(Base):
        __tablename__ = "vendors"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(256), unique=True)
        contact_person: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
        phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
        email: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    return {
        "ProductCategory": ProductCategory,
        "Product": Product,
        "Warehouse": Warehouse,
        "Stock": Stock,
        "StockMovement": StockMovement,
        "EquipmentAssignment": EquipmentAssignment,
        "Vendor": Vendor
    }
