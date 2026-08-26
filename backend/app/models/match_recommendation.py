from sqlalchemy import Column, String, Text, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class MatchRecommendation(Base, TimestampMixin):
    """Recommendation from a match analysis."""
    
    __tablename__ = "match_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False)
    
    category = Column(String(50), nullable=False)  # Skill, Experience, Certification, etc.
    priority = Column(String(20), nullable=True)  # HIGH, MEDIUM, LOW
    
    recommendation = Column(Text, nullable=False)
    action_required = Column(String(500), nullable=True)
    
    impact = Column(String(20), nullable=True)  # HIGH, MEDIUM, LOW
    difficulty = Column(String(20), nullable=True)  # HIGH, MEDIUM, LOW
    
    # Relationships
    match = relationship("Match", back_populates="recommendations")
