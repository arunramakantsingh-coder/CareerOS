from sqlalchemy import Column, String, Text, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base, TimestampMixin


class PersonaSuggestion(Base, TimestampMixin):
    """A proposed positioning lens over the canonical Career Vault facts."""
    __tablename__ = "persona_suggestions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    role_family = Column(String(120), nullable=True)
    positioning = Column(Text, nullable=True)
    target_titles = Column(JSON, nullable=True)
    supporting_fact_ids = Column(JSON, nullable=True)
    supporting_document_ids = Column(JSON, nullable=True)
    missing_evidence = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=False, default=0.5)
    reason = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="suggested")
