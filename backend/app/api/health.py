from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.health import HealthCheckResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    db_status = "unhealthy"
    
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        # Log error but don't expose details
        pass
    
    return HealthCheckResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        database=db_status,
        version="0.1.0",
    )
