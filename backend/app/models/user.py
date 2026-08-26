from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    locale = Column(String(10), default="en-US")
    timezone = Column(String(50), default="UTC")
    consent_flags = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    
    candidate_location = Column(String(255), nullable=True)
    candidate_timezone = Column(String(50), nullable=True)
    candidate_authorization = Column(JSON, nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    career_profiles = relationship("CareerProfile", back_populates="user")
    career_preferences = relationship("CareerPreference", back_populates="user", uselist=False)
    personas = relationship("Persona", back_populates="user")
    jobs = relationship("Job", back_populates="user")
    matches = relationship("Match", back_populates="user")
    resumes = relationship("ResumeVersion", back_populates="user")
    job_sources = relationship("JobSource", back_populates="user")
    job_listings = relationship("JobListing", back_populates="user")
    discoveries = relationship("JobDiscovery", back_populates="user")
    remote_eligibilities = relationship("RemoteEligibility", back_populates="user")
    migration_profiles = relationship("MigrationProfile", back_populates="user", uselist=False)
