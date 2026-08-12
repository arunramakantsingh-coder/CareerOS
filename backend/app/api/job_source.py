from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.job_source import JobSource
from app.models.job_source_connection import JobSourceConnection
from app.models.job_listing import JobListing
from app.models.user import User
from app.schemas.job_source import (
    JobSourceCreate, JobSourceUpdate, JobSourceResponse,
    JobSourceConnectionCreate, JobSourceConnectionResponse,
    JobListingResponse, IngestionRequest, IngestionResponse, IngestionStats
)
from app.utils.test_connector import TestConnector
from app.utils.ingestion_pipeline import IngestionPipeline

router = APIRouter(prefix="/sources", tags=["job_sources"])


@router.post("/", response_model=JobSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    source_data: JobSourceCreate,
    db: Session = Depends(get_db)
):
    """Create a new job source."""
    
    if source_data.user_id:
        user = db.query(User).filter(User.id == source_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    
    source = JobSource(
        user_id=source_data.user_id,
        name=source_data.name,
        source_type=source_data.source_type,
        config=source_data.config,
        is_active=source_data.is_active,
        is_system=source_data.is_system
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    
    return source


@router.get("/", response_model=List[JobSourceResponse])
async def list_sources(
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """List job sources for a user."""
    query = db.query(JobSource)
    
    if user_id:
        query = query.filter(JobSource.user_id == user_id)
    else:
        query = query.filter(JobSource.is_system == True)
    
    sources = query.all()
    return sources


@router.get("/{source_id}", response_model=JobSourceResponse)
async def get_source(
    source_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific job source."""
    source = db.query(JobSource).filter(JobSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job source not found"
        )
    return source


@router.post("/{source_id}/connections", response_model=JobSourceConnectionResponse)
async def add_connection(
    source_id: UUID,
    connection_data: JobSourceConnectionCreate,
    db: Session = Depends(get_db)
):
    """Add a connection to a job source."""
    source = db.query(JobSource).filter(JobSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job source not found"
        )
    
    connection = JobSourceConnection(
        source_id=source_id,
        connection_type=connection_data.connection_type,
        credentials=connection_data.credentials,
        endpoint=connection_data.endpoint,
        headers=connection_data.headers,
        is_valid=connection_data.is_valid,
        expires_at=connection_data.expires_at
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    
    return connection


@router.post("/{source_id}/ingest", response_model=IngestionResponse)
async def ingest_jobs(
    source_id: UUID,
    request: IngestionRequest,
    db: Session = Depends(get_db)
):
    """Trigger job ingestion for a source."""
    source = db.query(JobSource).filter(JobSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job source not found"
        )
    
    if not source.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job source is not active"
        )
    
    # Select connector based on source type
    if source.source_type == "test":
        connector = TestConnector(str(source.id), source.config or {})
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported source type: {source.source_type}"
        )
    
    # Validate connection
    if not await connector.validate_connection():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection validation failed"
        )
    
    # Run ingestion
    pipeline = IngestionPipeline(db)
    stats = await pipeline.ingest_from_connector(source, connector, request.params)
    
    return IngestionResponse(
        source_id=source_id,
        status=source.sync_status or "success",
        stats=stats,
        timestamp=datetime.now()
    )


@router.get("/{source_id}/listings", response_model=List[JobListingResponse])
async def get_source_listings(
    source_id: UUID,
    db: Session = Depends(get_db)
):
    """Get listings from a source."""
    listings = db.query(JobListing).filter(
        JobListing.source_id == source_id,
        JobListing.status == "active"
    ).order_by(JobListing.posted_at.desc()).all()
    
    return listings


@router.put("/{source_id}", response_model=JobSourceResponse)
async def update_source(
    source_id: UUID,
    source_data: JobSourceUpdate,
    db: Session = Depends(get_db)
):
    """Update a job source."""
    source = db.query(JobSource).filter(JobSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job source not found"
        )
    
    for key, value in source_data.dict(exclude_unset=True).items():
        setattr(source, key, value)
    
    db.commit()
    db.refresh(source)
    
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a job source."""
    source = db.query(JobSource).filter(JobSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job source not found"
        )
    
    db.delete(source)
    db.commit()
    
    return None
