from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, Text, JSON, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class ResumeEvidenceLink(Base, TimestampMixin):
    """Links between resume statements and Career Evidence."""
    
    __tablename__ = "resume_evidence_links"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey("resume_sections.id"), nullable=False)
    
    statement = Column(Text, nullable=False)  # The resume statement
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("career_evidence.id"), nullable=True)
    
    # Evidence reference
    source_type = Column(String(50), nullable=True)  # employment, project, certification, etc.
    source_reference = Column(JSON, nullable=True)  # {id, name, date, etc.}
    
    # Verification
    is_verified = Column(Boolean, default=False)
    confidence = Column(Float, default=1.0)
    
    # Explanation
    explanation = Column(Text, nullable=True)  # Why this evidence supports this statement
    
    # Relationships
    section = relationship("ResumeSection", back_populates="evidence_links")
