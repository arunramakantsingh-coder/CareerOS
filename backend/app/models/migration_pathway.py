from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class MigrationPathway(Base, TimestampMixin):
    """Migration pathway (combination of visa + conditions)."""
    
    __tablename__ = "migration_pathways"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    visa_id = Column(UUID(as_uuid=True), ForeignKey("visas.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    pathway_type = Column(String(50), nullable=False)  # skilled, employer-sponsored, family, etc.
    
    # Requirements
    requirements = Column(JSON, nullable=True)  # Structured requirements
    points_required = Column(Integer, nullable=True)
    
    # Eligibility
    is_active = Column(Boolean, default=True)
    is_current = Column(Boolean, default=True)
    
    # Relationships
    visa = relationship("Visa", back_populates="pathways")
