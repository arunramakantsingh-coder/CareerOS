from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class Tenant(Base):
    """Tenant model for multi-tenant SaaS."""
    
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    plan = Column(String(50), default="free")
    status = Column(String(20), default="active")
    settings = Column(String(2000), nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)