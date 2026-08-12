from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, Integer, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    """Professional project entry."""
    
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    career_profile_id = Column(UUID(as_uuid=True), ForeignKey("career_profiles.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    role = Column(String(255), nullable=True)
    technologies = Column(JSON, nullable=True)  # List of technologies used
    
    responsibilities = Column(JSON, nullable=True)  # List of responsibilities
    achievements = Column(JSON, nullable=True)  # List of achievements
    
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_current = Column(Boolean, default=False)
    
    client = Column(String(255), nullable=True)
    team_size = Column(Integer, nullable=True)
    
    # Relationships
    career_profile = relationship("CareerProfile", back_populates="projects")
