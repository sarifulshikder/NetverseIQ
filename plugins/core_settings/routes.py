"""Core Settings Plugin — FastAPI Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db as _get_db
from api.deps import get_current_user
from models.user import User
from typing import List, Dict, Any

router = APIRouter(prefix="/api/p/core_settings", tags=["Plugin: Core_Settings"])

# Models will be injected via get_router
models = {}


def get_router(injected_models: Dict[str, Any]):
    global models
    models = injected_models

    Setting = models["Setting"]
    SMSGateway = models["SMSGateway"]
    EmailConfig = models["EmailConfig"]
    PaymentGateway = models["PaymentGateway"]
    CompanyProfile = models["CompanyProfile"]

    # ── Settings Endpoints ────────────────────────────────────
    @router.get("/all", summary="Get all settings")
    async def get_all_settings(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(Setting))
        return result.scalars().all()

    @router.get("/{group}", summary="Get settings by group")
    async def get_settings_by_group(group: str, db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(Setting).where(Setting.group == group))
        return result.scalars().all()

    @router.put("/{key}", summary="Update setting by key")
    async def update_setting(key: str, body: Dict[str, Any], db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(Setting).where(Setting.key == key))
        setting = result.scalar_one_or_none()
        if not setting:
            # Create if not exists? Roadmap says PUT /api/p/settings/{key}
            setting = Setting(key=key, value=body.get("value", ""), group=body.get("group", "general"))
            db.add(setting)
        else:
            if "value" in body:
                setting.value = body["value"]
            if "group" in body:
                setting.group = body["group"]
            if "description" in body:
                setting.description = body["description"]
        
        await db.commit()
        await db.refresh(setting)
        return setting

    # ── Company Profile Endpoints ──────────────────────────────
    @router.get("/company", summary="Get company profile")
    async def get_company_profile(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(CompanyProfile).limit(1))
        profile = result.scalar_one_or_none()
        if not profile:
            return {}
        return profile

    @router.put("/company", summary="Update company profile")
    async def update_company_profile(body: Dict[str, Any], db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(CompanyProfile).limit(1))
        profile = result.scalar_one_or_none()
        if not profile:
            profile = CompanyProfile(**body)
            db.add(profile)
        else:
            for k, v in body.items():
                if hasattr(profile, k) and k != "id":
                    setattr(profile, k, v)
        
        await db.commit()
        await db.refresh(profile)
        return profile

    # ── SMS Gateway Endpoints ─────────────────────────────────
    @router.get("/sms/gateways", summary="List SMS gateways")
    async def list_sms_gateways(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(SMSGateway))
        return result.scalars().all()

    @router.post("/sms/test", summary="Test SMS gateway")
    async def test_sms(body: Dict[str, Any], current_user: User = Depends(get_current_user)):
        # Placeholder for actual SMS sending logic
        return {"status": "success", "message": "Test SMS sent (mock)"}

    # ── Email Settings Endpoints ──────────────────────────────
    @router.get("/email/configs", summary="List email configurations")
    async def list_email_configs(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(EmailConfig))
        return result.scalars().all()

    @router.post("/email/test", summary="Test Email settings")
    async def test_email(body: Dict[str, Any], current_user: User = Depends(get_current_user)):
        # Placeholder for actual Email sending logic
        return {"status": "success", "message": "Test email sent (mock)"}

    # ── Payment Gateway Endpoints ─────────────────────────────
    @router.get("/payment-gateways", summary="List payment gateways")
    async def list_payment_gateways(db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(PaymentGateway))
        return result.scalars().all()

    @router.put("/payment-gateways/{id}", summary="Update payment gateway")
    async def update_payment_gateway(id: int, body: Dict[str, Any], db: AsyncSession = Depends(_get_db), current_user: User = Depends(get_current_user)):
        result = await db.execute(select(PaymentGateway).where(PaymentGateway.id == id))
        gateway = result.scalar_one_or_none()
        if not gateway:
            raise HTTPException(404, "Payment gateway not found")
        for k, v in body.items():
            if hasattr(gateway, k) and k != "id":
                setattr(gateway, k, v)
        await db.commit()
        await db.refresh(gateway)
        return gateway

    return router


