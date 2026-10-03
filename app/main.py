from fastapi import FastAPI

from app.database.database import engine
from app.database.base import Base
from app.api.routes.users import router as user_router

from app.models import (
    User,
    Organization,
    OrganizationMember,
    Team,
    TeamMember,
    Role,
    Permission,
    RolePermission,
    EmailOTP,
    DataSource,
)

from app.api.routes.auth import router as auth_router
from app.api.routes.teams import router as team_router
from app.api.routes.organizations import router as organization_router
from app.api.routes.rbac import router as rbac_router
from app.api.routes.data_sources import router as data_source_router
from app.api.routes.projects import router as project_router
from app.api.routes.rag import router as rag_router
from app.api.routes.ml_data_preparation import router as ml_data_preparation_router
from app.api.routes.ml_models import router as ml_models_router
from app.api.routes.risk_engine import router as risk_engine_router
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Zero Trust Security Monitoring Platform",
    description="P4 Backend APIs",
    version="1.0.0"
)


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(organization_router)
app.include_router(team_router)
app.include_router(project_router)
app.include_router(rbac_router)
app.include_router(data_source_router)
app.include_router(rag_router)
app.include_router(ml_data_preparation_router)
app.include_router(ml_models_router)
app.include_router(risk_engine_router)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "success": True,
        "message": "Zero Trust API is running"
    }


@app.get("/ui")
def ui():
    index_file = os.path.join(static_dir, "index.html")
    return FileResponse(index_file)


@app.get("/health")
def health_check():
    return {
        "success": True,
        "message": "API is healthy"
    }