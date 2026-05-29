# NetverseIQ — Plugin Development Guide

## Plugin Contract

Every plugin must live in `/plugins/<plugin_id>/` and contain at minimum:
- `manifest.json` — metadata + sidebar menu definition
- `plugin.py` — Python module with a `register(app, Base)` function

## manifest.json Schema

```json
{
  "id": "unique-plugin-id",
  "name": "Human Readable Name",
  "version": "1.0.0",
  "description": "What this plugin does",
  "author": "Author Name",
  "enabled": true,
  "menu": [
    {
      "label": "Sidebar Label",
      "icon": "LucideIconName",
      "path": "/frontend-route",
      "permissions": ["plugin:read"]
    }
  ],
  "permissions": ["plugin:read", "plugin:write"],
  "api_prefix": "/api/p/plugin-id"
}
```

Available Lucide icons for `menu.icon`: Users, FileText, Receipt, Bell,
BarChart2, Puzzle, Settings, Shield, Activity, Wifi, Star, Zap, Globe, Map, ...

## plugin.py Structure

```python
def register(app, Base):
    """
    Called once at startup by PluginLoader.
    
    app  — FastAPI application instance
    Base — SQLAlchemy DeclarativeBase (shared with core)
    """
    # 1. Define your models
    from sqlalchemy import Integer, String
    from sqlalchemy.orm import Mapped, mapped_column

    class MyModel(Base):
        __tablename__ = "my_plugin_table"
        __table_args__ = {"extend_existing": True}
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        name: Mapped[str] = mapped_column(String(256))

    # 2. Define your routes
    from fastapi import APIRouter, Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from database import get_db

    router = APIRouter(prefix="/api/p/myplugin", tags=["My Plugin"])

    @router.get("/")
    async def list_items(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(MyModel))
        return result.scalars().all()

    # 3. Mount router
    app.include_router(router)
```

## Tables

Plugin tables are created automatically by SQLAlchemy at startup.
Always use `__table_args__ = {"extend_existing": True}` to avoid errors on hot-reload.

## Frontend Integration

Add your frontend pages to `frontend/src/pages/MyPage.jsx` and register the
route in `frontend/src/App.jsx`. The sidebar menu is automatically built from
enabled plugins' `manifest.json` menu items.
