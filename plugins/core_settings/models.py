"""Core Settings Plugin — SQLAlchemy Models"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional


def register_models(Base):
    """Register Core Settings models with the shared SQLAlchemy Base."""

    class Setting(Base):
        __tablename__ = "settings"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        key: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
        value: Mapped[str] = mapped_column(Text, nullable=False)
        group: Mapped[str] = mapped_column(String(64), index=True, default="general")
        description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )

    class SMSGateway(Base):
        __tablename__ = "sms_gateways"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        provider: Mapped[str] = mapped_column(String(64), nullable=False)
        api_key: Mapped[str] = mapped_column(String(256), nullable=False)
        sender_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        config_json: Mapped[dict] = mapped_column(JSON, default={})
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class EmailConfig(Base):
        __tablename__ = "email_configs"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        smtp_host: Mapped[str] = mapped_column(String(256), nullable=False)
        port: Mapped[int] = mapped_column(Integer, default=587)
        username: Mapped[str] = mapped_column(String(256), nullable=False)
        password: Mapped[str] = mapped_column(String(256), nullable=False)
        use_tls: Mapped[bool] = mapped_column(Boolean, default=True)
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class PaymentGateway(Base):
        __tablename__ = "payment_gateways"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(64), nullable=False)
        config_json: Mapped[dict] = mapped_column(JSON, default={})
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        mode: Mapped[str] = mapped_column(String(32), default="sandbox")  # sandbox or production
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class CompanyProfile(Base):
        __tablename__ = "company_profile"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(256), nullable=False)
        address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        logo: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
        phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
        email: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
        trade_license: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
        tin_number: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
        updated_at: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )

    return {
        "Setting": Setting,
        "SMSGateway": SMSGateway,
        "EmailConfig": EmailConfig,
        "PaymentGateway": PaymentGateway,
        "CompanyProfile": CompanyProfile
    }
