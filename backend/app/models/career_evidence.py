from datetime import datetime
from sqlalchemy import Column, DateTime, String, Text, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class CareerEvidence(Base, TimestampMixin):
    """Evidence linking career claims to their sources."""
    
    __tablename__ = "career_evidence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    career_profile_id = Column(UUID(as_uuid=True), ForeignKey("career_profiles.id"), nullable=False)
    
    claim = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=False)
    
    source_id = Column(UUID(as_uuid=True), nullable=True)
    source_entity = Column(String(50), nullable=True)
    
    source_file = Column(String(500), nullable=True)
    excerpt = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String(100), nullable=True)
    
    meta_data = Column(JSON, nullable=True)  # Renamed from 'metadata'
    
    career_profile = relationship("CareerProfile", back_populates="evidence_entries")
