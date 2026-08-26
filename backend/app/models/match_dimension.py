from sqlalchemy import Column, String, Float, Text, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class MatchDimension(Base, TimestampMixin):
    """Individual dimension score for a match."""
    
    __tablename__ = "match_dimensions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False)
    
    name = Column(String(50), nullable=False)  # Technical, Experience, Architecture, etc.
    score = Column(Float, nullable=False)  # 0-100
    weight = Column(Float, nullable=False)  # Weight applied
    
    # Details
    matched_items = Column(JSON, nullable=True)
    partial_items = Column(JSON, nullable=True)
    missing_items = Column(JSON, nullable=True)
    
    explanation = Column(Text, nullable=True)
    
    # Relationships
    match = relationship("Match", back_populates="dimensions")
