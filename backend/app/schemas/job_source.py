from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseResponse


class JobSourceCreate(BaseModel):
    """Schema for creating a job source."""
    user_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=100)
    source_type: str = Field(..., description="api, rss, email, url, test")
    config: Optional[Dict[str, Any]] = None
    is_active: bool = True
    is_system: bool = False


class JobSourceUpdate(BaseModel):
    """Schema for updating a job source."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_system: Optional[bool] = None


class JobSourceResponse(BaseResponse):
    """Schema for job source response."""
    id: UUID
    user_id: Optional[UUID]
    name: str
    source_type: str
    config: Optional[Dict[str, Any]]
    is_active: bool
    is_system: bool
    last_sync: Optional[datetime]
    sync_status: Optional[str]
    total_listings: int
    error_count: int
    last_error: Optional[str]


class JobSourceConnectionCreate(BaseModel):
    """Schema for creating a source connection."""
    connection_type: str
    credentials: Optional[str] = None
    endpoint: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    is_valid: bool = False
    expires_at: Optional[datetime] = None


class JobSourceConnectionResponse(BaseResponse):
    """Schema for source connection response."""
    id: UUID
    source_id: UUID
    connection_type: str
    endpoint: Optional[str]
    headers: Optional[Dict[str, str]]
    is_valid: bool
    last_used: Optional[datetime]
    expires_at: Optional[datetime]


class JobListingResponse(BaseResponse):
    """Schema for job listing response."""
    id: UUID
    user_id: Optional[UUID]
    source_id: Optional[UUID]
    external_id: Optional[str]
    external_url: Optional[str]
    title: str
    company: Optional[str]
    location: Optional[str]
    description: Optional[str]
    status: str
    is_duplicate: bool
    posted_at: Optional[datetime]
    last_seen_at: Optional[datetime]


class IngestionRequest(BaseModel):
    """Request for job ingestion."""
    params: Optional[Dict[str, Any]] = None


class IngestionStats(BaseModel):
    """Statistics from ingestion."""
    fetched: int
    created: int
    updated: int
    duplicates: int
    errors: int


class IngestionResponse(BaseModel):
    """Response for job ingestion."""
    source_id: UUID
    status: str
    stats: IngestionStats
    timestamp: datetime
