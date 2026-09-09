from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class ProfessionalExperience(Base, TimestampMixin):
    """Canonical professional employment fact."""
    
    __tablename__ = "professional_experiences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidate_profiles.id"), nullable=False)
    
    company = Column(String(255), nullable=False)
    client = Column(String(255), nullable=True)
    title = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_current = Column(Boolean, default=False)
    
    responsibilities = Column(JSON, nullable=True)  # List of responsibilities
    achievements = Column(JSON, nullable=True)  # List of achievements
    technologies = Column(JSON, nullable=True)  # List of technologies/capabilities evidenced by the role
    
    industry = Column(String(100), nullable=True)
    industries = Column(JSON, nullable=True)  # Multiple industry signals when present
    company_size = Column(String(50), nullable=True)
    
    # Source
    source_type = Column(String(50), nullable=True)  # cv, linkedin, user, document
    source_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciliation_status = Column(String(30), nullable=True)  # extracted, ai_reconciled, ai_review, conflicting, user_confirmed
    
    # Relationships
    candidate = relationship("CandidateProfile", back_populates="experiences")
