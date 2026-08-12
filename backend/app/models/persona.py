from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Persona(Base, TimestampMixin):
    """Career Persona - different market positioning based on same career facts."""
    
    __tablename__ = "personas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    career_profile_id = Column(UUID(as_uuid=True), ForeignKey("career_profiles.id"), nullable=False)
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    
    # Targeting
    target_titles = Column(JSON, nullable=True)
    target_industries = Column(JSON, nullable=True)
    target_locations = Column(JSON, nullable=True)
    target_companies = Column(JSON, nullable=True)
    
    # Preferences
    preferred_seniority = Column(String(50), nullable=True)
    salary_preferences = Column(JSON, nullable=True)
    remote_preference = Column(String(20), nullable=True)
    migration_preference = Column(String(20), nullable=True)
    
    # Weighting configuration
    skill_weights = Column(JSON, nullable=True)
    capability_weights = Column(JSON, nullable=True)
    
    # Additional configuration
    keywords = Column(JSON, nullable=True)
    positioning = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="personas")
    career_profile = relationship("CareerProfile", back_populates="personas")
    skill_weights_entries = relationship("PersonaSkillWeight", back_populates="persona")
    matches = relationship("Match", back_populates="persona", cascade="all, delete-orphan")
    resumes = relationship("ResumeVersion", back_populates="persona", cascade="all, delete-orphan")
