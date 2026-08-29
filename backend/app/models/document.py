from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.models.base import Base, TimestampMixin


class Document(Base, TimestampMixin):
    """Professional document stored in the Vault."""
    
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidate_profiles.id"), nullable=False)
    
    # Original file
    original_filename = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(50), nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Content hash for deduplication
    content_hash = Column(String(64), nullable=True)  # SHA-256
    
    # Storage
    storage_path = Column(String(500), nullable=False)
    storage_url = Column(String(500), nullable=True)
    
    # Classification
    document_category = Column(String(50), nullable=True)  # cv, employment, certification, education, project, identity, other
    document_subcategory = Column(String(50), nullable=True)  # offer_letter, experience_letter, payslip, etc.
    document_type = Column(String(50), nullable=True)
    
    # Metadata
    issuer = Column(String(255), nullable=True)
    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    document_number = Column(String(255), nullable=True)
    
    # Status
    status = Column(String(20), default="uploaded")  # uploaded, processing, processed, failed, classified, extracted
    processing_status = Column(JSON, nullable=True)
    extraction_status = Column(String(20), default="pending")
    extraction_id = Column(UUID(as_uuid=True), nullable=True)
    
    # ZIP ingestion
    batch_id = Column(UUID(as_uuid=True), nullable=True)
    is_zip_content = Column(Boolean, default=False)
    parent_zip_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Provenance
    source = Column(String(50), nullable=True)  # upload, import, scan, zip
    source_metadata = Column(JSON, nullable=True)
    
    # Classification confidence
    classification_confidence = Column(Float, nullable=True)
    
    # Relationships
    candidate = relationship("CandidateProfile", back_populates="documents")
    extraction = relationship("ExtractionResult", back_populates="document")
