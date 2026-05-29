"""
NetverseIQ — Database Seeder
Creates default admin user and roles if they don't already exist.
Safe to run on every startup (idempotent).
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import settings
from models.user import User, Role
from services.auth_service import hash_password

logger = logging.getLogger(__name__)

DEFAULT_ROLES = [
    {"name": "admin",    "description": "Full system access",          "permissions": "*"},
    {"name": "staff",    "description": "Manage customers and billing","permissions": "customer:*,billing:*"},
    {"name": "readonly", "description": "View-only access",            "permissions": "*.read"},
]


async def seed_database(db: AsyncSession) -> None:
    """Idempotently seed roles and default admin user."""

    # ── Seed Roles ────────────────────────────────────────────
    for role_data in DEFAULT_ROLES:
        result = await db.execute(select(Role).where(Role.name == role_data["name"]))
        if result.scalar_one_or_none() is None:
            db.add(Role(**role_data))
            logger.info(f"Created role: {role_data['name']}")

    await db.flush()

    # ── Seed Admin User ───────────────────────────────────────
    result = await db.execute(select(User).where(User.email == settings.ADMIN_EMAIL))
    if result.scalar_one_or_none() is None:
        admin_role_result = await db.execute(select(Role).where(Role.name == "admin"))
        admin_role = admin_role_result.scalar_one_or_none()

        admin = User(
            name=settings.ADMIN_NAME,
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            is_superuser=True,
            is_active=True,
        )
        if admin_role:
            admin.roles = [admin_role]
        db.add(admin)
        logger.info(f"Created default admin user: {settings.ADMIN_EMAIL}")

    await db.commit()
    logger.info("Database seeding complete.")
