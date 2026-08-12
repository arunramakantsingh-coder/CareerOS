from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, Integer, Text, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Employment(Base, TimestampMixin):
    """Employment history entry."""
    
    __tablename__ = "employments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    career_profile_id = Column(UUID(as_uuid=True), ForeignKey("career_profiles.id"), nullable=False)
    
    company = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    is_current = Column(Boolean, default=False)
    
    responsibilities = Column(Text, nullable=True)
    achievements = Column(JSON, nullable=True)  # List of achievements
    
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    
    # Relationships
    career_profile = relationship("CareerProfile", back_populates="employments")
