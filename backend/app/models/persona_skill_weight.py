from sqlalchemy import Column, String, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class PersonaSkillWeight(Base, TimestampMixin):
    """Skill weights for a specific persona."""
    
    __tablename__ = "persona_skill_weights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    persona_id = Column(UUID(as_uuid=True), ForeignKey("personas.id"), nullable=False)
    
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    weight = Column(Float, default=1.0)  # 0.0 to 2.0 multiplier
    importance = Column(Integer, default=1)  # 1-5 importance scale
    
    # Additional context
    notes = Column(String(500), nullable=True)
    
    # Relationships
    persona = relationship("Persona", back_populates="skill_weights_entries")
    skill = relationship("Skill", back_populates="persona_weights")
