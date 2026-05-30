# NetverseIQ 🌐
**Next-Gen Plug & Play ISP Billing & Management Platform**

---

## ⚡ Quick Start (Ubuntu / any Docker host)

```bash
# 1. Clone / extract the project
cd netverseiq

# 2. Copy environment config
cp .env.example .env      # already pre-filled with defaults

# 3. Launch everything with one command
docker compose up -d --build

# 4. Open in browser
http://localhost
```

### Default Login
| Field    | Value                  |
|----------|------------------------|
| Email    | admin@netverseiq.local |
| Password | Admin1234              |

> Change credentials in `.env` before production deployment!

---

## 🏗️ Architecture

```
Browser → Nginx (port 80)
             ├── /api/*  →  FastAPI Backend (port 8000)
             │               ├── Core: Auth, Users, Plugin Manager
             │               └── Plugins: Customer, Billing, Notifications, Analytics
             └── /*      →  React Frontend (Vite build)
Backend ←→ PostgreSQL (port 5432, internal)
Backend ←→ Redis (port 6379, internal)
```

---

## 🧩 Plugin System

Each plugin lives in `/plugins/<name>/` and contains:

| File            | Purpose                                      |
|-----------------|----------------------------------------------|
| `manifest.json` | Plugin metadata, menu items, permissions     |
| `plugin.py`     | `register(app, Base)` — mounts routes+models |

### How Plugins Work

- **Backend:** Plugins are auto-discovered on startup. Add `plugin.py` + `manifest.json`, restart backend — routes are live.
- **Frontend:** The sidebar menu is fully dynamic — it reads from `/api/plugins/menu` automatically. New plugins appear in the menu without any frontend changes.
- **Generic UI:** If a plugin has a `/list` endpoint, the built-in `PluginPage` component will display, add, edit, and delete records automatically — no new page needed.
- **Custom UI:** For complex plugins (like Customers, Billing), a dedicated page can be created in `frontend/src/pages/` and registered in `App.jsx`.

### Built-in Plugins

| Plugin        | API Prefix              | Features                          |
|---------------|-------------------------|-----------------------------------|
| customer      | `/api/p/customer/`      | Customer CRUD, search, stats      |
| billing       | `/api/p/billing/`       | Invoices, payment tracking        |
| notification  | `/api/p/notification/`  | Send & log notifications          |
| analytics     | `/api/p/analytics/`     | KPIs, revenue trend, growth       |
| subscription  | `/api/p/subscription/`  | Subscriptions, renewals           |
| packages      | `/api/p/packages/`      | ISP package management            |
| inventory     | `/api/p/inventory/`     | Equipment inventory               |
| expense       | `/api/p/expense/`       | Expense tracking                  |
| support       | `/api/p/support/`       | Support tickets                   |

### Creating a New Plugin (Backend only — UI is automatic!)

```bash
mkdir plugins/myplugin
```

**`plugins/myplugin/manifest.json`**
```json
{
  "id": "myplugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "Does amazing things",
  "author": "You",
  "enabled": true,
  "menu": [
    { "label": "My Page", "icon": "Star", "path": "myplugin" }
  ],
  "api_prefix": "/api/p/myplugin"
}
```

**`plugins/myplugin/plugin.py`**
```python
def register(app, Base):
    from fastapi import APIRouter, Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select, Integer, String, update, delete
    from sqlalchemy.orm import Mapped, mapped_column
    from database import get_db

    class MyModel(Base):
        __tablename__ = "myplugin_items"
        __table_args__ = {"extend_existing": True}
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(256))

    router = APIRouter(prefix="/api/p/myplugin", tags=["My Plugin"])

    @router.get("/list")
    async def list_items(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(MyModel))
        items = result.scalars().all()
        return {"total": len(items), "items": [{"id": i.id, "name": i.name} for i in items]}

    @router.post("/")
    async def create_item(body: dict, db: AsyncSession = Depends(get_db)):
        item = MyModel(**body)
        db.add(item); await db.commit(); await db.refresh(item)
        return {"id": item.id, "name": item.name}

    @router.put("/{item_id}")
    async def update_item(item_id: int, body: dict, db: AsyncSession = Depends(get_db)):
        await db.execute(update(MyModel).where(MyModel.id == item_id).values(**body))
        await db.commit()
        return {"ok": True}

    @router.delete("/{item_id}", status_code=204)
    async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
        await db.execute(delete(MyModel).where(MyModel.id == item_id))
        await db.commit()

    app.include_router(router)
```

Then restart backend only:
```bash
docker compose restart backend
```

✅ The new plugin will appear in the sidebar and show a full data table automatically — **no frontend changes needed!**

---

## 🔧 Useful Commands

```bash
# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Restart only backend (after plugin changes)
docker compose restart backend

# Rebuild frontend (only needed for core UI changes)
docker compose build frontend && docker compose up -d frontend

# Stop everything
docker compose down

# Stop + remove data (full reset)
docker compose down -v

# Access DB directly
docker compose exec db psql -U netverseiq -d netverseiq
```

---

## 📡 API Documentation

Visit: **http://localhost/api/docs** (Swagger UI)

---

## 📁 Folder Structure

```
netverseiq/
├── core/                  # FastAPI backend (microkernel)
│   ├── main.py            # App entry point
│   ├── plugin_loader.py   # Auto-discovers & loads plugins
│   ├── api/routes/        # Core routes: auth, users, plugins, health
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Auth service (JWT, password)
├── frontend/              # React + Vite + TailwindCSS
│   └── src/
│       ├── App.jsx        # Router (static + dynamic plugin routes)
│       ├── pages/         # Dashboard, Customers, Billing, etc.
│       │   └── PluginPage.jsx  # Generic page for new plugins (auto UI)
│       ├── components/    # Layout, Sidebar (dynamic menu), Header
│       └── store/         # Zustand: auth + theme
├── plugins/               # All feature plugins (add yours here!)
│   ├── customer/
│   ├── billing/
│   ├── subscription/
│   └── ...
├── nginx/                 # Reverse proxy config
├── docker-compose.yml
└── .env                   # Environment configuration
```

---

## 🔐 Security Notes for Production

1. Change `SECRET_KEY` and `JWT_SECRET_KEY` in `.env`
2. Change `ADMIN_PASSWORD` in `.env`
3. Change `DB_PASSWORD` in `.env`
4. Set `DEBUG=false`
5. Restrict `CORS_ORIGINS` to your domain

---

*NetverseIQ v1.0.0 — Built with FastAPI + React + PostgreSQL*
