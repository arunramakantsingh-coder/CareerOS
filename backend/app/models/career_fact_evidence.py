from sqlalchemy import Column, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base, TimestampMixin


class CareerFactEvidence(Base, TimestampMixin):
    """Many-to-many evidence links between canonical candidate facts and source documents."""
    __tablename__ = "career_fact_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    fact_type = Column(String(50), nullable=False)
    fact_id = Column(UUID(as_uuid=True), nullable=False)
    relationship = Column(String(40), nullable=False, default="supports")
    confidence = Column(Float, nullable=False, default=0.7)
    excerpt = Column(Text, nullable=True)
