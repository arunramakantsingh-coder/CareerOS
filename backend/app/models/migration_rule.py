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
    
    rule_key = Column(String(100), nullable=False)
    rule_type = Column(String(50), nullable=False)
    rule_value = Column(JSON, nullable=False)
    
    description = Column(Text, nullable=True)
    condition_text = Column(Text, nullable=True)
    
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime, nullable=True)
    is_current = Column(Boolean, default=True)
    
    source_type = Column(String(50), nullable=True)
    source_url = Column(String(500), nullable=True)
    source_reference = Column(String(255), nullable=True)
    
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String(100), nullable=True)
    
    meta_data = Column(JSON, nullable=True)  # ✅ Renamed from 'metadata'
    priority = Column(Integer, default=1)
    
    visa = relationship("Visa", back_populates="rules")
