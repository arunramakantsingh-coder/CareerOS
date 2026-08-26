from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class JobListing(Base, TimestampMixin):
    """A job listing ingested from a source."""
    
    __tablename__ = "job_listings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("job_sources.id"), nullable=True)
    
    external_id = Column(String(255), nullable=True)
    external_url = Column(String(500), nullable=True)
    
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    parsed_title = Column(String(255), nullable=True)
    parsed_company = Column(String(255), nullable=True)
    parsed_location = Column(String(255), nullable=True)
    
    status = Column(String(20), default="active")
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(UUID(as_uuid=True), nullable=True)
    
    posted_at = Column(DateTime, nullable=True)
    last_seen_at = Column(DateTime, nullable=True)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    
    source_metadata = Column(JSON, nullable=True)
    fingerprint = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="job_listings")
    source = relationship("JobSource", back_populates="listings")
