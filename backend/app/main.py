import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, health_check
from app.core.config import settings
from app.core.database import engine
from app.models import base
from app.utils.logging import setup_logging

# Setup logging
setup_logging(settings.LOG_LEVEL)

# Create tables (in development)
# In production, use Alembic migrations
if settings.ENVIRONMENT == "development":
    base.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger = logging.getLogger(__name__)
    logger.info(f"Starting CareerOS API in {settings.ENVIRONMENT} mode")
    yield
    # Shutdown
    logger.info("Shutting down CareerOS API")


# Create FastAPI app
app = FastAPI(
    title="CareerOS API",
    version="0.1.0",
    description="AI-Powered Global Career Operating System",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(health_check.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "CareerOS API",
        "version": "0.1.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
    }
