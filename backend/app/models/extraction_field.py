from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class ExtractionField(Base, TimestampMixin):
    """Individual field extracted from a document."""

    __tablename__ = "extraction_fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    extraction_id = Column(UUID(as_uuid=True), ForeignKey("extraction_results.id"), nullable=False)

    # Field identification
    field_key = Column(String(100), nullable=False)
    field_category = Column(String(50), nullable=True)

    # Value
    value = Column(Text, nullable=True)
    value_type = Column(String(50), nullable=True)  # string, number, date, array, object

    # Source
    source_text = Column(Text, nullable=True)  # Original text from document
    source_location = Column(String(100), nullable=True)  # Page, line, etc.

    # Confidence
    confidence = Column(Float, nullable=True)  # 0-1
    confidence_reason = Column(Text, nullable=True)

    # Status
    extraction_status = Column(String(20), default="extracted")  # extracted, inferred, conflicting, missing, user_confirmed

    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciliation_status = Column(String(20), nullable=True)

    # Metadata
    # SQLAlchemy reserves the Python attribute name `metadata` on declarative models.
    # Keep the existing database column name while exposing it as a safe Python attribute.
    extraction_metadata = Column("metadata", JSON, nullable=True)

    # Relationships
    extraction = relationship("ExtractionResult", back_populates="field_extra")
