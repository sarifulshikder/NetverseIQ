"""
NetverseIQ Core — Plugin Registry Model
Tracks all discovered plugins and their enabled/disabled state.
"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class PluginRegistry(Base):
    """Persisted record of each discovered plugin."""
    __tablename__ = "plugin_registry"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    plugin_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    description: Mapped[str] = mapped_column(Text, default="")
    author: Mapped[str] = mapped_column(String(128), default="")
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    manifest: Mapped[dict] = mapped_column(JSON, default=dict)
    installed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
