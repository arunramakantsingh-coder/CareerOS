from sqlalchemy import Column, String, Text, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Country(Base, TimestampMixin):
    """Country master data for migration."""
    
    __tablename__ = "countries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    code = Column(String(2), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=True)
    
    immigration_authority = Column(String(255), nullable=True)
    official_website = Column(String(500), nullable=True)
    
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    meta_data = Column(JSON, nullable=True)  # ✅ Renamed from 'metadata'
    
    visas = relationship("Visa", back_populates="country", cascade="all, delete-orphan")
    occupation_mappings = relationship("OccupationMapping", back_populates="country", cascade="all, delete-orphan")
