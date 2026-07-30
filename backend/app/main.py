"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables (for dev; production uses Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    root_path="/qingtian/api/v1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register routers
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.projects import router as projects_router
from app.api.plans import router as plans_router
from app.api.tasks import router as tasks_router
from app.api.requirements import router as requirements_router
from app.api.defects import router as defects_router
from app.api.dashboard import router as dashboard_router
from app.api.reviews import router as reviews_router
from app.api.notifications import router as notifications_router
from app.api.templates import router as templates_router

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(projects_router, prefix="/projects", tags=["Projects"])
app.include_router(plans_router, prefix="/plans", tags=["Plans"])
app.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
app.include_router(requirements_router, prefix="/requirements", tags=["Requirements"])
app.include_router(defects_router, prefix="/defects", tags=["Defects"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
app.include_router(templates_router, prefix="/templates", tags=["Templates"])


@app.get("/")
async def root():
    return {"code": 200, "message": f"{settings.APP_NAME} API v{settings.APP_VERSION}"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}
