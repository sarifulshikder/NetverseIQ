"""
NetverseIQ — Core API
FastAPI microkernel: auth, users, roles, plugins, activity log.
All business features live in /plugins.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import engine, Base, AsyncSessionLocal
from plugin_loader import PluginLoader
from event_bus import EventBus
from scheduler import setup_scheduler
from seed import seed_database
from api.routes import auth, users, plugins, health, activity, roles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("netverseiq")
plugin_loader = PluginLoader()
event_bus = EventBus(settings.REDIS_URL)
scheduler = setup_scheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info(f"  {settings.APP_NAME} v{settings.APP_VERSION}  starting up")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Store event bus in app state
    app.state.event_bus = event_bus
    
    # Start scheduler
    scheduler.start()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Core database tables ready.")
    async with AsyncSessionLocal() as db:
        await seed_database(db)
    await plugin_loader.discover_and_load(app)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("NetverseIQ is ready ✓")
    yield
    await event_bus.close()
    scheduler.shutdown()
    await engine.dispose()
    logger.info("NetverseIQ shut down gracefully.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Next-Gen Plug & Play ISP Billing & Management Platform.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router,    prefix="/api/health",   tags=["Health"])
app.include_router(auth.router,      prefix="/api/auth",     tags=["Authentication"])
app.include_router(users.router,     prefix="/api/users",    tags=["Users"])
app.include_router(roles.router,     prefix="/api/roles",    tags=["Roles & RBAC"])
app.include_router(plugins.router,   prefix="/api/plugins",  tags=["Plugins"])
app.include_router(activity.router,  prefix="/api/activity", tags=["Activity Log"])


@app.get("/api", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "plugins_loaded": plugin_loader.loaded,
    }
