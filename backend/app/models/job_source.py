from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class JobSource(Base, TimestampMixin):
    """Configuration for a job source connector."""
    
    __tablename__ = "job_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    name = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)
    config = Column(JSON, nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)
    last_sync = Column(DateTime, nullable=True)
    sync_status = Column(String(20), nullable=True)
    
    total_listings = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="job_sources")
    connections = relationship("JobSourceConnection", back_populates="source", cascade="all, delete-orphan")
    listings = relationship("JobListing", back_populates="source", cascade="all, delete-orphan")
