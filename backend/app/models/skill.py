from sqlalchemy import Column, String, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Skill(Base, TimestampMixin):
    """Skill entry."""
    
    __tablename__ = "skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    career_profile_id = Column(UUID(as_uuid=True), ForeignKey("career_profiles.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)  # Technical, Soft, Leadership, etc.
    proficiency = Column(String(20), nullable=True)  # Beginner, Intermediate, Advanced, Expert
    years_experience = Column(Float, nullable=True)
    last_used = Column(String(10), nullable=True)  # Year string
    
    description = Column(Text, nullable=True)
    is_core = Column(String(10), default="false")  # true/false
    
    # Relationships
    career_profile = relationship("CareerProfile", back_populates="skills")
    persona_weights = relationship("PersonaSkillWeight", back_populates="skill")
