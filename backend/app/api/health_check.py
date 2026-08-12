from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["health"])


@router.get("/ping")
async def ping():
    """Simple ping endpoint."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "message": "pong",
    }
