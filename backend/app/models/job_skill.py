from sqlalchemy import Column, String, Text, ForeignKey, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class JobSkill(Base, TimestampMixin):
    """Skill extracted from a job posting."""
    
    __tablename__ = "job_skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    skill_name = Column(String(100), nullable=False)
    skill_category = Column(String(50), nullable=True)  # Technical, Soft, Leadership
    
    # Requirement level
    is_mandatory = Column(Boolean, default=False)
    is_preferred = Column(Boolean, default=False)
    
    # Proficiency needed
    proficiency_required = Column(String(20), nullable=True)  # Beginner, Intermediate, Advanced, Expert
    years_required = Column(Float, nullable=True)
    
    # Context
    context = Column(Text, nullable=True)  # How the skill is mentioned in the JD
    
    # Relationships
    job = relationship("Job", back_populates="job_skills")
