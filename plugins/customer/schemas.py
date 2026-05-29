"""Customer Plugin — Pydantic Schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str = ""
    address: str = ""
    area_zone: str = ""
    connection_id: str = ""
    package_name: str = ""
    monthly_fee: float = 0.0
    ip_address: str = ""
    mac_address: str = ""
    notes: str = ""


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    area_zone: Optional[str] = None
    status: Optional[str] = None
    package_name: Optional[str] = None
    monthly_fee: Optional[float] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    notes: Optional[str] = None


class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    address: str
    area_zone: str
    connection_id: str
    status: str
    package_name: str
    monthly_fee: float
    ip_address: str
    mac_address: str
    notes: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
