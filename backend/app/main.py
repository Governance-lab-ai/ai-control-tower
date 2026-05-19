from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ai_systems import router as ai_systems_router
from app.api.governance import router as governance_router
from app.api.health import router as health_router
from app.api.model_runs import router as model_runs_router
from app.api.prompt_versions import router as prompt_versions_router
from app.core.config import get_settings
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.app_env == "local":
        init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs" if settings.app_env == "local" else None,
        redoc_url="/redoc" if settings.app_env == "local" else None,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(ai_systems_router)
    app.include_router(governance_router)
    app.include_router(model_runs_router)
    app.include_router(prompt_versions_router)
    return app


app = create_app()
