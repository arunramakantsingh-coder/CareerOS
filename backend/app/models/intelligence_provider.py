from sqlalchemy import Column, String, Text, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base, TimestampMixin


class IntelligenceProviderConfig(Base, TimestampMixin):
    """Global CareerOS Intelligence provider configuration.

    This is platform configuration, not user-owned career data. API credentials
    are encrypted at rest and are never serialized back to clients.
    """

    __tablename__ = "intelligence_provider_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String(50), unique=True, nullable=False, index=True)
    label = Column(String(120), nullable=False)
    category = Column(String(30), nullable=False, default="cloud")
    model = Column(String(255), nullable=True)
    base_url = Column(String(500), nullable=True)
    encrypted_api_key = Column(Text, nullable=True)
    api_key_last4 = Column(String(8), nullable=True)
    configured = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=False, index=True)
    priority = Column(Integer, nullable=False, default=100)
    capabilities = Column(JSON, nullable=True)
    routing_policy = Column(JSON, nullable=True)
    last_tested_at = Column(String(40), nullable=True)
    last_test_status = Column(String(30), nullable=True)
    last_error = Column(Text, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
