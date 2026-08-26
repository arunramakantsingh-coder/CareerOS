from datetime import datetime
from sqlalchemy import Column, DateTime, String, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Certification(Base, TimestampMixin):
    """Professional certification entry."""
    
    __tablename__ = "certifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    career_profile_id = Column(UUID(as_uuid=True), ForeignKey("career_profiles.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=False)
    
    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    credential_reference = Column(String(255), nullable=True)
    
    credential_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(String(10), default="true")  # true/false
    
    # Relationships
    career_profile = relationship("CareerProfile", back_populates="certifications")
