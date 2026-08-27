from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class CandidateSkill(Base, TimestampMixin):
    """Candidate skill entry."""
    
    __tablename__ = "candidate_skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidate_profiles.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)  # Technical, Soft, Leadership, etc.
    proficiency = Column(String(20), nullable=True)  # Beginner, Intermediate, Advanced, Expert
    years_experience = Column(Float, nullable=True)
    last_used = Column(String(10), nullable=True)
    
    # Source
    source_type = Column(String(50), nullable=True)
    source_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Confidence
    confidence = Column(Float, nullable=True)
    
    # Relationships
    candidate = relationship("CandidateProfile", back_populates="skills")
