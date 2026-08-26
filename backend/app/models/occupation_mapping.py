from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class OccupationMapping(Base, TimestampMixin):
    """Occupation mapping for migration."""
    
    __tablename__ = "occupation_mappings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_id = Column(UUID(as_uuid=True), ForeignKey("countries.id"), nullable=False)
    
    # Occupation codes
    anzsc_code = Column(String(20), nullable=True)  # ANZSCO code
    local_code = Column(String(20), nullable=True)  # Country-specific code
    
    # Occupation details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # Professional, Technical, etc.
    skill_level = Column(Integer, nullable=True)  # 1-5
    skill_type = Column(String(50), nullable=True)  # Manager, Professional, etc.
    
    # Migration relevance
    is_in_demand = Column(Boolean, default=False)
    is_sponsorship_eligible = Column(Boolean, default=False)
    is_skills_assessment_required = Column(Boolean, default=True)
    
    # Assessment authority
    assessing_authority = Column(String(255), nullable=True)
    assessing_website = Column(String(500), nullable=True)
    
    # Relationships
    country = relationship("Country", back_populates="occupation_mappings")
