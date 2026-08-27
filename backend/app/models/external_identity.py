from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.models.base import Base, TimestampMixin


class ExternalIdentity(Base, TimestampMixin):
    """External identity for OAuth/SSO providers."""
    
    __tablename__ = "external_identities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    provider = Column(String(50), nullable=False)  # google, linkedin, apple, etc.
    provider_user_id = Column(String(255), nullable=False)
    provider_email = Column(String(255), nullable=True)
    
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    # Provider-specific metadata
    provider_data = Column(JSON, nullable=True)
    scopes = Column(JSON, nullable=True)
    
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="external_identities")
