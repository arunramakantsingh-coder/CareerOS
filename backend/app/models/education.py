from datetime import datetime
from sqlalchemy import Column, DateTime, String, Text, Float, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Education(Base, TimestampMixin):
    """Education entry."""
    
    __tablename__ = "educations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    career_profile_id = Column(UUID(as_uuid=True), ForeignKey("career_profiles.id"), nullable=False)
    
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    field_of_study = Column(String(255), nullable=True)
    
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_current = Column(String(10), default="false")  # true/false
    
    grade = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    achievements = Column(Text, nullable=True)
    
    # Relationships
    career_profile = relationship("CareerProfile", back_populates="educations")
