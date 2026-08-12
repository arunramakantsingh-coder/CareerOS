from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class JobResponsibility(Base, TimestampMixin):
    """Responsibility extracted from a job posting."""
    
    __tablename__ = "job_responsibilities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)  # Technical, Leadership, Operational, Strategic
    
    # Priority/order
    order = Column(Integer, nullable=True)
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    job = relationship("Job", back_populates="responsibilities")
