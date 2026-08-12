from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Match(Base, TimestampMixin):
    """Career-to-Job match result."""
    
    __tablename__ = "matches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    persona_id = Column(UUID(as_uuid=True), ForeignKey("personas.id"), nullable=False)
    
    # Overall score
    overall_score = Column(Float, nullable=False)  # 0-100
    
    # Dimension scores (0-100 each)
    dimension_scores = Column(JSON, nullable=False)  # {"Technical": 85, "Experience": 90, ...}
    
    # Status
    status = Column(String(20), nullable=True)  # MATCHED, PARTIAL, MISSING, RISK
    
    # Summary
    summary = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    
    # Match details
    matched_skills = Column(JSON, nullable=True)
    partial_skills = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    hard_failures = Column(JSON, nullable=True)
    
    # Gap analysis
    gaps = Column(JSON, nullable=True)  # {"Technical": ["skill1", "skill2"], ...}
    risks = Column(JSON, nullable=True)  # ["skill gap", "experience gap", ...]
    
    # Relationships
    user = relationship("User", back_populates="matches")
    job = relationship("Job", back_populates="matches")
    persona = relationship("Persona", back_populates="matches")
    dimensions = relationship("MatchDimension", back_populates="match", cascade="all, delete-orphan")
    recommendations = relationship("MatchRecommendation", back_populates="match", cascade="all, delete-orphan")
