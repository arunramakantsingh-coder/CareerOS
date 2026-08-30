from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class CandidateCertification(Base, TimestampMixin):
    """Candidate certification entry."""
    
    __tablename__ = "candidate_certifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidate_profiles.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=False)
    
    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    credential_reference = Column(String(255), nullable=True)
    
    credential_url = Column(String(500), nullable=True)
    
    # Source
    source_type = Column(String(50), nullable=True)
    source_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Confidence
    confidence = Column(Float, nullable=True)
    
    # Relationships
    candidate = relationship("CandidateProfile", back_populates="certifications")
