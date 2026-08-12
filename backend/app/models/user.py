from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    locale = Column(String(10), default="en-US")
    timezone = Column(String(50), default="UTC")
    consent_flags = Column(String(500), nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    career_profiles = relationship("CareerProfile", back_populates="user")
    career_preferences = relationship("CareerPreference", back_populates="user", uselist=False)
