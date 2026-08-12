from sqlalchemy import Column, String, Boolean, Text, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class JobSourceConnection(Base, TimestampMixin):
    """Connection details for a job source."""
    
    __tablename__ = "job_source_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("job_sources.id"), nullable=False)
    
    connection_type = Column(String(50), nullable=False)
    credentials = Column(Text, nullable=True)
    endpoint = Column(String(500), nullable=True)
    headers = Column(JSON, nullable=True)
    
    is_valid = Column(Boolean, default=False)
    last_used = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    source = relationship("JobSource", back_populates="connections")
