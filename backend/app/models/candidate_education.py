from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, DateTime, Float, Float, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class CandidateEducation(Base, TimestampMixin):
    """Candidate education entry."""
    
    __tablename__ = "candidate_educations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidate_profiles.id"), nullable=False)
    
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    field_of_study = Column(String(255), nullable=True)
    
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_current = Column(Boolean, default=False)
    
    grade = Column(String(50), nullable=True)
    
    source_type = Column(String(50), nullable=True)
    source_id = Column(UUID(as_uuid=True), nullable=True)
    
    confidence = Column(Float, nullable=True)
    
    candidate = relationship("CandidateProfile", back_populates="educations")


