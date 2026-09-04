import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, health_check, auth, oauth, persona, persona_skill_weight, job, match, resume, job_source, discovery, remote, migration, candidate, document, document_intake, extraction, profile_intelligence, v01_product, identity, developer
from app.core.config import settings
from app.core.database import engine
from app.models import base
from app.utils.logging import setup_logging

setup_logging(settings.LOG_LEVEL)
if settings.ENVIRONMENT == "development": base.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.getLogger(__name__).info(f"Starting CareerOS API in {settings.ENVIRONMENT} mode")
    yield
    logging.getLogger(__name__).info("Shutting down CareerOS API")

app = FastAPI(title="CareerOS API", version="0.1.0", description="AI-Powered Global Career Operating System", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}):3000$",
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
for router in (health.router, health_check.router, auth.router, oauth.router, persona.router, persona_skill_weight.router, job.router, match.router, resume.router, job_source.router, discovery.router, remote.router, migration.router, candidate.router, document.router, document_intake.router, extraction.router, profile_intelligence.router, v01_product.router, identity.router, developer.router):
    app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"name":"CareerOS API","version":"0.1.0","status":"operational","environment":settings.ENVIRONMENT}
