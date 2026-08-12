from datetime import datetime
from sqlalchemy import Column, DateTime, String, Text, JSON, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Achievement(Base, TimestampMixin):
    """Achievement entry."""
    
    __tablename__ = "achievements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    career_profile_id = Column(UUID(as_uuid=True), ForeignKey("career_profiles.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    date = Column(DateTime, nullable=True)
    category = Column(String(50), nullable=True)  # Award, Recognition, Publication, etc.
    
    metrics = Column(JSON, nullable=True)  # {metric: value, unit: ...}
    context = Column(Text, nullable=True)
    
    # Relationships
    career_profile = relationship("CareerProfile", back_populates="achievements")
