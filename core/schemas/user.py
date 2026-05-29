from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class RoleOut(BaseModel):
    id: int
    name: str
    description: str
    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    is_superuser: bool = False


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    roles: List[RoleOut] = []
    model_config = {"from_attributes": True}
