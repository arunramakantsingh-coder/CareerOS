from sqlalchemy import Column, String, Text, JSON, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.models.base import Base, TimestampMixin


class SkillGapObservation(Base, TimestampMixin):
    """Records a skill gap observed during job analysis."""
    
    __tablename__ = "skill_gap_observations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    skill_name = Column(String(255), nullable=False)
    skill_category = Column(String(50), nullable=True)
    
    # Gap classification
    gap_type = Column(String(50), nullable=False)  # missing, mandatory_missing, partial
    
    # Context
    job_analysis_id = Column(UUID(as_uuid=True), nullable=True)  # Link to analysis run
    context = Column(JSON, nullable=True)  # How skill was referenced in job
    
    # Tracking
    is_recurring = Column(Boolean, default=False)
    recurrence_count = Column(Integer, default=1)
    
    # Relationships
    user = relationship("User", back_populates="skill_gaps")
    job = relationship("Job", back_populates="skill_gaps")


class SkillGapAggregate(Base, TimestampMixin):
    """Aggregated skill gap data per user."""
    
    __tablename__ = "skill_gap_aggregates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    skill_name = Column(String(255), nullable=False)
    skill_category = Column(String(50), nullable=True)
    
    # Aggregation
    occurrence_count = Column(Integer, default=0)
    job_count = Column(Integer, default=0)  # Unique jobs where gap appeared
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    
    # Gap classification
    primary_gap_type = Column(String(50), nullable=True)  # Most common gap type
    is_critical = Column(Boolean, default=False)
    
    # Metadata
    context_summary = Column(JSON, nullable=True)  # Aggregated context
    
    # Relationships
    user = relationship("User", back_populates="skill_gap_aggregates")
