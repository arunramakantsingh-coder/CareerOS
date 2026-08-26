import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth,
    discovery,
    health,
    health_check,
    job,
    job_source,
    match,
    migration,
    persona,
    persona_skill_weight,
    remote,
    resume,
    v01_product,
)
from app.core.config import settings
from app.core.database import engine
from app.models import base
from app.utils.logging import setup_logging

setup_logging(settings.LOG_LEVEL)

if settings.ENVIRONMENT == "development":
    base.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = logging.getLogger(__name__)
    logger.info("Starting CareerOS API in %s mode", settings.ENVIRONMENT)
    yield
    logger.info("Shutting down CareerOS API")


app = FastAPI(
    title="CareerOS API",
    version="0.1.0",
    description="AI-Powered Global Career Operating System",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(health_check.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(persona.router, prefix="/api/v1")
app.include_router(persona_skill_weight.router, prefix="/api/v1")
app.include_router(job.router, prefix="/api/v1")
app.include_router(match.router, prefix="/api/v1")
app.include_router(resume.router, prefix="/api/v1")
app.include_router(job_source.router, prefix="/api/v1")
app.include_router(discovery.router, prefix="/api/v1")
app.include_router(remote.router, prefix="/api/v1")
app.include_router(migration.router, prefix="/api/v1")
app.include_router(v01_product.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": "CareerOS API",
        "version": "0.1.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
    }
