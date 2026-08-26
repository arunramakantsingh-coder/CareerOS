from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class CareerProfile(Base, TimestampMixin):
    """Career profile for a user - main career identity."""
    
    __tablename__ = "career_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Basic info
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Career targeting
    target_roles = Column(JSON, nullable=True)  # List of target role titles
    seniority = Column(String(50), nullable=True)  # Entry, Mid, Senior, Lead, Manager, Director, Executive
    years_experience = Column(Integer, nullable=True)
    
    # Preferences
    preferred_locations = Column(JSON, nullable=True)  # List of preferred locations
    remote_preference = Column(String(20), nullable=True)  # On-site, Hybrid, Remote, Any
    salary_preferences = Column(JSON, nullable=True)  # Min, max, currency
    
    # Additional
    industries = Column(JSON, nullable=True)  # List of industries
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="career_profiles")
    employments = relationship("Employment", back_populates="career_profile")
    projects = relationship("Project", back_populates="career_profile")
    skills = relationship("Skill", back_populates="career_profile")
    certifications = relationship("Certification", back_populates="career_profile")
    educations = relationship("Education", back_populates="career_profile")
    achievements = relationship("Achievement", back_populates="career_profile")
    technologies = relationship("Technology", back_populates="career_profile")
    evidence_entries = relationship("CareerEvidence", back_populates="career_profile")
    personas = relationship("Persona", back_populates="career_profile")
