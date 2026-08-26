from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Job(Base, TimestampMixin):
    """Job posting - raw and processed."""
    
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    source_id = Column(String(255), nullable=True)
    source_url = Column(String(500), nullable=True)
    source_name = Column(String(100), nullable=True)
    
    raw_jd = Column(Text, nullable=False)
    
    title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    company_description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    remote_policy = Column(String(50), nullable=True)
    
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(3), nullable=True)
    salary_period = Column(String(20), nullable=True)
    
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    job_dna = relationship("JobDNA", back_populates="job", uselist=False, cascade="all, delete-orphan")
    job_skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    responsibilities = relationship("JobResponsibility", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="job", cascade="all, delete-orphan")
    resumes = relationship("ResumeVersion", back_populates="job", cascade="all, delete-orphan")
    discoveries = relationship("JobDiscovery", back_populates="job", cascade="all, delete-orphan")
    remote_eligibilities = relationship("RemoteEligibility", back_populates="job", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGapObservation", back_populates="job", cascade="all, delete-orphan")
