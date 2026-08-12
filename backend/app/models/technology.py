from sqlalchemy import Column, String, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Technology(Base, TimestampMixin):
    """Technology skill entry."""
    
    __tablename__ = "technologies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    career_profile_id = Column(UUID(as_uuid=True), ForeignKey("career_profiles.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    vendor = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)  # Programming, Cloud, Network, Security, etc.
    
    proficiency = Column(String(20), nullable=True)  # Beginner, Intermediate, Advanced, Expert
    years_experience = Column(Float, nullable=True)
    last_used = Column(String(10), nullable=True)
    
    certifications = Column(JSON, nullable=True)  # List of related certifications
    projects_used = Column(JSON, nullable=True)  # List of project names
    
    # Relationships
    career_profile = relationship("CareerProfile", back_populates="technologies")
