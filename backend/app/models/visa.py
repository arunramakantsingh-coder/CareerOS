from sqlalchemy import Column, String, Text, JSON, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Visa(Base, TimestampMixin):
    """Visa type master data."""
    
    __tablename__ = "visas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_id = Column(UUID(as_uuid=True), ForeignKey("countries.id"), nullable=False)
    
    code = Column(String(50), nullable=False)  # Visa code (e.g., 189, 482, etc.)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=True)  # Skilled, Student, Family, etc.
    
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    country = relationship("Country", back_populates="visas")
    rules = relationship("MigrationRule", back_populates="visa", cascade="all, delete-orphan")
    pathways = relationship("MigrationPathway", back_populates="visa", cascade="all, delete-orphan")
