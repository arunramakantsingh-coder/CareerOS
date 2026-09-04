from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, DateTime, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import Base, TimestampMixin


class Document(Base, TimestampMixin):
    """Professional document stored in the evidence library."""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidate_profiles.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(50), nullable=True)
    mime_type = Column(String(100), nullable=True)
    storage_path = Column(String(500), nullable=False)
    storage_url = Column(String(500), nullable=True)
    document_category = Column(String(50), nullable=True)
    document_subcategory = Column(String(50), nullable=True)
    document_type = Column(String(50), nullable=True)
    status = Column(String(20), default="uploaded")
    processing_status = Column(JSON, nullable=True)
    extraction_status = Column(String(20), default="pending")
    extraction_id = Column(UUID(as_uuid=True), nullable=True)
    source = Column(String(50), nullable=True)
    source_metadata = Column(JSON, nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)
    issuer = Column(String(255), nullable=True)
    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    document_number = Column(String(255), nullable=True)
    batch_id = Column(UUID(as_uuid=True), nullable=True)
    is_zip_content = Column(Boolean, default=False)
    parent_zip_id = Column(UUID(as_uuid=True), nullable=True)
    classification_confidence = Column(Float, nullable=True)

    # Evidence-library presentation and human-review metadata.
    user_label = Column(String(255), nullable=True)
    detected_type = Column(String(80), nullable=True)
    classification_reason = Column(Text, nullable=True)
    verification_status = Column(String(30), nullable=False, default="reported")
    processing_stage = Column(String(40), nullable=False, default="uploaded")

    candidate = relationship("CandidateProfile", back_populates="documents")
    extraction = relationship("ExtractionResult", back_populates="document")
