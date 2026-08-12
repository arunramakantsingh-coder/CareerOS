from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class ResumeVersion(Base, TimestampMixin):
    """Resume version generated for a specific job and persona."""
    
    __tablename__ = "resume_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    persona_id = Column(UUID(as_uuid=True), ForeignKey("personas.id"), nullable=False)
    
    # Version tracking
    version_number = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, default=True)
    is_preview = Column(Boolean, default=False)
    
    # Resume content
    content = Column(Text, nullable=False)  # Full resume text
    format_type = Column(String(20), default="ats")  # ats, standard, executive
    
    # ATS optimization
    ats_score = Column(Float, nullable=True)  # 0-100
    keyword_coverage = Column(Float, nullable=True)  # 0-100
    
    # Metadata
    generation_notes = Column(Text, nullable=True)
    truth_score = Column(Float, nullable=True)  # 0-100 - evidence verification score
    
    # Status
    status = Column(String(20), default="draft")  # draft, reviewed, approved
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    job = relationship("Job", back_populates="resumes")
    persona = relationship("Persona", back_populates="resumes")
    sections = relationship("ResumeSection", back_populates="resume", cascade="all, delete-orphan")
