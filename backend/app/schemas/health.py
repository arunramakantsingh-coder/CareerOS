from pydantic import BaseModel
from typing import Optional


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    
    status: str
    database: Optional[str] = None
    version: str


class SystemInfoResponse(BaseModel):
    """System information response."""
    
    name: str
    version: str
    environment: str
    status: str