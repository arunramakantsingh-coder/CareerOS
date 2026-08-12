from sqlalchemy import Column, String, Float, JSON, ForeignKey, DateTime, Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.models.base import Base, TimestampMixin


class JobDiscovery(Base, TimestampMixin):
    """Semantic job discovery result for a user."""
    
    __tablename__ = "job_discoveries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    # Discovery scores (0-100)
    overall_score = Column(Float, nullable=False)
    title_match = Column(Float, nullable=True)
    capability_match = Column(Float, nullable=True)
    skill_match = Column(Float, nullable=True)
    responsibility_match = Column(Float, nullable=True)
    career_match = Column(Float, nullable=True)
    
    # Detailed breakdown
    capability_details = Column(JSON, nullable=True)
    skill_details = Column(JSON, nullable=True)
    responsibility_details = Column(JSON, nullable=True)
    career_details = Column(JSON, nullable=True)
    
    # Semantic discovery metadata
    discovery_rank = Column(Integer, nullable=True)
    discovery_confidence = Column(Float, nullable=True)
    matched_capabilities = Column(JSON, nullable=True)
    missing_capabilities = Column(JSON, nullable=True)
    
    # Status
    is_viewed = Column(Boolean, default=False)
    is_saved = Column(Boolean, default=False)
    is_applied = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="discoveries")
    job = relationship("Job", back_populates="discoveries")
