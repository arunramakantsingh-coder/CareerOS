from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.models.base import Base, TimestampMixin


class ExtractionResult(Base, TimestampMixin):
    """AI extraction result from a document."""
    
    __tablename__ = "extraction_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidate_profiles.id"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    
    # Extraction metadata
    extraction_type = Column(String(50), nullable=False)  # cv, document, profile
    extraction_version = Column(String(20), nullable=True)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    
    # Extracted data
    extracted_data = Column(JSON, nullable=False)  # Structured extracted data
    confidence_scores = Column(JSON, nullable=True)  # Per-field confidence
    
    # Status
    status = Column(String(20), default="pending")  # pending, processing, complete, failed, reviewed
    error_message = Column(Text, nullable=True)
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciled_at = Column(DateTime, nullable=True)
    
    # Relationships
    candidate = relationship("CandidateProfile", back_populates="extractions")
    document = relationship("Document", back_populates="extraction")
    field_extra = relationship("ExtractionField", back_populates="extraction", cascade="all, delete-orphan")
