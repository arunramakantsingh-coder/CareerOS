from sqlalchemy import Column, String, Text, JSON, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class CapabilityTaxonomy(Base, TimestampMixin):
    """Taxonomy of capabilities for job matching."""
    
    __tablename__ = "capability_taxonomy"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=True)  # Technical, Leadership, Domain, etc.
    description = Column(Text, nullable=True)
    
    # Hierarchical relationships
    parent_id = Column(UUID(as_uuid=True), ForeignKey("capability_taxonomy.id"), nullable=True)
    
    # Synonyms and related terms
    synonyms = Column(JSON, nullable=True)  # List of related terms
    keywords = Column(JSON, nullable=True)  # Keywords for matching
    
    # Metadata
    is_active = Column(Boolean, default=True)
    importance = Column(Integer, default=1)  # 1-5
    
    # Relationships
    parent = relationship("CapabilityTaxonomy", remote_side=[id], backref="children")
