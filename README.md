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
| Field    | Value                     |
|----------|---------------------------|
| Email    | admin@netverseiq.local    |
| Password | Admin@1234                |

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

**Plugins are auto-discovered on startup.** No restart needed after adding a plugin file — just restart the backend container.

### Built-in Plugins
| Plugin        | API Prefix              | Features                          |
|---------------|-------------------------|-----------------------------------|
| customer      | `/api/p/customer/`      | Customer CRUD, search, stats      |
| billing       | `/api/p/billing/`       | Invoices, payment tracking, stats |
| notification  | `/api/p/notification/`  | Send & log notifications          |
| analytics     | `/api/p/analytics/`     | KPIs, revenue trend, growth       |

### Creating a New Plugin

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
    { "label": "My Page", "icon": "Star", "path": "/myplugin" }
  ]
}
```

**`plugins/myplugin/plugin.py`**
```python
def register(app, Base):
    from fastapi import APIRouter
    router = APIRouter(prefix="/api/p/myplugin", tags=["My Plugin"])

    @router.get("/")
    async def hello():
        return {"hello": "from myplugin"}

    app.include_router(router)
```

Then restart backend: `docker compose restart backend`

---

## 🔧 Useful Commands

```bash
# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Restart only backend (after plugin changes)
docker compose restart backend

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
├── core/               # FastAPI backend (microkernel)
│   ├── main.py         # App entry point
│   ├── plugin_loader.py# Auto-discovers & loads plugins
│   ├── api/routes/     # Core routes: auth, users, plugins, health
│   ├── models/         # SQLAlchemy models (User, Role, PluginRegistry)
│   ├── schemas/        # Pydantic schemas
│   └── services/       # Auth service (JWT, password)
├── frontend/           # React + Vite + TailwindCSS
│   └── src/
│       ├── App.jsx     # Router + auth guard
│       ├── pages/      # Dashboard, Customers, Billing, etc.
│       ├── components/ # Layout, Sidebar, Header, StatCard
│       └── store/      # Zustand: auth + theme
├── plugins/            # All feature plugins (add yours here)
│   ├── customer/
│   ├── billing/
│   ├── notification/
│   └── analytics/
├── nginx/              # Reverse proxy config
├── docs/               # Additional documentation
├── docker-compose.yml
└── .env                # Environment configuration
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
