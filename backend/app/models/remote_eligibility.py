from sqlalchemy import Column, String, Float, JSON, ForeignKey, DateTime, Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.models.base import Base, TimestampMixin


class RemoteEligibility(Base, TimestampMixin):
    """Remote eligibility evaluation for a job."""
    
    __tablename__ = "remote_eligibilities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    # Classification
    remote_classification = Column(String(50), nullable=True)  # worldwide, country-specific, region-specific, us-only, eu-only, uk-only, india-only, unknown
    
    # Scores (0-100)
    overall_remote_score = Column(Float, nullable=False)
    timezone_score = Column(Float, nullable=True)
    authorization_score = Column(Float, nullable=True)
    sponsorship_score = Column(Float, nullable=True)
    contractor_score = Column(Float, nullable=True)
    relocation_score = Column(Float, nullable=True)
    
    # Detailed analysis
    remote_analysis = Column(JSON, nullable=True)
    restrictions = Column(JSON, nullable=True)  # List of restrictions
    requirements = Column(JSON, nullable=True)  # List of requirements
    
    # Eligibility flags
    is_remote_eligible = Column(Boolean, default=False)
    is_timezone_compatible = Column(Boolean, default=False)
    has_work_authorization = Column(Boolean, default=False)
    requires_sponsorship = Column(Boolean, default=False)
    requires_relocation = Column(Boolean, default=False)
    allows_contractor = Column(Boolean, default=False)
    allows_eor = Column(Boolean, default=False)
    
    # Candidate context
    candidate_location = Column(String(255), nullable=True)
    candidate_timezone = Column(String(50), nullable=True)
    candidate_authorization = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="remote_eligibilities")
    job = relationship("Job", back_populates="remote_eligibilities")
