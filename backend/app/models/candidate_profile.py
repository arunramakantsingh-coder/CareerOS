from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class CandidateProfile(Base, TimestampMixin):
    """Canonical candidate profile."""
    
    __tablename__ = "candidate_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Personal
    full_name = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    
    # Contact
    linkedin_url = Column(String(500), nullable=True)
    linkedin_username = Column(String(255), nullable=True)
    primary_email = Column(String(255), nullable=True)
    primary_phone = Column(String(50), nullable=True)
    
    # Work preferences
    work_preferences = Column(JSON, nullable=True)
    
    # Professional
    years_experience = Column(Float, nullable=True)
    industries = Column(JSON, nullable=True)
    seniority = Column(String(50), nullable=True)
    
    # Profile completeness (cached)
    completeness_score = Column(Float, nullable=True)
    completeness_breakdown = Column(JSON, nullable=True)
    
    # Reconciliation status
    reconciliation_status = Column(String(20), default="pending")
    
    # Metadata
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="candidate_profile")
    documents = relationship("Document", back_populates="candidate", cascade="all, delete-orphan")
    extractions = relationship("ExtractionResult", back_populates="candidate", cascade="all, delete-orphan")
    experiences = relationship("ProfessionalExperience", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    certifications = relationship("CandidateCertification", back_populates="candidate", cascade="all, delete-orphan")
    educations = relationship("CandidateEducation", back_populates="candidate", cascade="all, delete-orphan")
