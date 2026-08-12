from datetime import datetime
from sqlalchemy import Column, DateTime, String, Text, JSON, Boolean, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class MigrationRule(Base, TimestampMixin):
    """Versioned immigration rule."""
    
    __tablename__ = "migration_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    visa_id = Column(UUID(as_uuid=True), ForeignKey("visas.id"), nullable=False)
    
    # Rule identification
    rule_key = Column(String(100), nullable=False)  # age, english, points, etc.
    rule_type = Column(String(50), nullable=False)  # requirement, condition, points
    
    # Rule value
    rule_value = Column(JSON, nullable=False)  # {"min": 18, "max": 45} or {"level": "Proficient"}
    
    # Description
    description = Column(Text, nullable=True)
    condition_text = Column(Text, nullable=True)  # Human-readable condition
    
    # Versioning
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime, nullable=True)
    is_current = Column(Boolean, default=True)
    
    # Source
    source_type = Column(String(50), nullable=True)  # legislation, policy, website
    source_url = Column(String(500), nullable=True)
    source_reference = Column(String(255), nullable=True)
    
    # Verification
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String(100), nullable=True)
    
    # Additional
    meta_data = Column(JSON, nullable=True)  # Renamed from 'metadata'
    priority = Column(Integer, default=1)  # 1-5 for rule importance
    
    # Relationships
    visa = relationship("Visa", back_populates="rules")
