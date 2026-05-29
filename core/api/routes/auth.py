"""NetverseIQ — Auth API Routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from api.deps import get_current_user
from models.user import User
from schemas.auth import LoginRequest, TokenResponse, TokenRefreshRequest
from schemas.user import UserOut
from services.auth_service import (
    authenticate_user, create_access_token, create_refresh_token,
    decode_token, get_user_by_id
)
from services.activity_service import log_activity

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    await log_activity(
        db, action="auth.login", user_id=user.id,
        detail=f"User '{user.email}' logged in",
        ip_address=request.client.host if request.client else "",
    )
    await db.commit()
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if payload is None or payload.type != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = await get_user_by_id(db, int(payload.sub))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
