"""
NetverseIQ — Role Management Routes
GET    /api/roles           → list roles
POST   /api/roles           → create role
PUT    /api/roles/{id}      → update role
DELETE /api/roles/{id}      → delete role
POST   /api/roles/{id}/assign/{user_id}  → assign role to user
DELETE /api/roles/{id}/assign/{user_id} → remove role from user
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from database import get_db
from api.deps import require_superuser
from models.user import User, Role

router = APIRouter()


class RoleCreate(BaseModel):
    name: str
    description: str = ""
    permissions: str = ""  # CSV: "customer:read,billing:read"


class RoleUpdate(BaseModel):
    name: str = None
    description: str = None
    permissions: str = None


def _role_out(role: Role) -> dict:
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "permissions": role.permissions,
    }


@router.get("/", summary="List all roles")
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_superuser),
):
    result = await db.execute(select(Role))
    return [_role_out(r) for r in result.scalars().all()]


@router.post("/", status_code=201, summary="Create role")
async def create_role(
    body: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_superuser),
):
    role = Role(**body.model_dump())
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return _role_out(role)


@router.put("/{role_id}", summary="Update role")
async def update_role(
    role_id: int,
    body: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_superuser),
):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(404, "Role not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(role, k, v)
    await db.commit()
    await db.refresh(role)
    return _role_out(role)


@router.delete("/{role_id}", status_code=204, summary="Delete role")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_superuser),
):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(404, "Role not found")
    await db.delete(role)
    await db.commit()


@router.post("/{role_id}/assign/{user_id}", summary="Assign role to user")
async def assign_role(
    role_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_superuser),
):
    role_r = await db.execute(select(Role).where(Role.id == role_id))
    role = role_r.scalar_one_or_none()
    user_r = await db.execute(select(User).where(User.id == user_id))
    user = user_r.scalar_one_or_none()
    if not role or not user:
        raise HTTPException(404, "Role or User not found")
    if role not in user.roles:
        user.roles.append(role)
    await db.commit()
    return {"ok": True, "message": f"Role '{role.name}' assigned to '{user.name}'"}


@router.delete("/{role_id}/assign/{user_id}", summary="Remove role from user")
async def remove_role(
    role_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_superuser),
):
    role_r = await db.execute(select(Role).where(Role.id == role_id))
    role = role_r.scalar_one_or_none()
    user_r = await db.execute(select(User).where(User.id == user_id))
    user = user_r.scalar_one_or_none()
    if not role or not user:
        raise HTTPException(404, "Role or User not found")
    if role in user.roles:
        user.roles.remove(role)
    await db.commit()
    return {"ok": True, "message": f"Role '{role.name}' removed from '{user.name}'"}
