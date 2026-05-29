"""
NetverseIQ — Permission Service
Checks if a user has a required permission based on their roles.

Permission format: "resource:action"
Examples: "customer:read", "billing:write", "plugin:manage"

Superusers bypass all permission checks.
Wildcard "*" in role permissions grants everything.
"customer:*" grants all customer permissions.
"""
from models.user import User


def has_permission(user: User, permission: str) -> bool:
    """Return True if user has the given permission."""
    if user.is_superuser:
        return True

    for role in user.roles:
        granted = [p.strip() for p in role.permissions.split(",") if p.strip()]
        for g in granted:
            if g == "*":
                return True
            if g == permission:
                return True
            # Wildcard: "customer:*" matches "customer:read"
            if g.endswith(":*"):
                prefix = g[:-2]
                if permission.startswith(prefix + ":"):
                    return True
    return False


def require_permission(permission: str):
    """
    FastAPI dependency factory.
    Usage: Depends(require_permission("customer:write"))
    """
    from fastapi import Depends, HTTPException
    from api.deps import get_current_user

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: '{permission}' required",
            )
        return current_user

    return checker
