from sqlalchemy import Column, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base, TimestampMixin


class EmailConnectorAccount(Base, TimestampMixin):
    """Provider-neutral mailbox connection state. Secrets remain in ExternalIdentity/Vault storage."""
    __tablename__ = "email_connector_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(40), nullable=False)
    email_address = Column(String(320), nullable=True)
    auth_method = Column(String(30), nullable=False, default="oauth2")
    status = Column(String(30), nullable=False, default="available")
    capabilities = Column(JSON, nullable=True)
    scopes = Column(JSON, nullable=True)
    external_identity_id = Column(UUID(as_uuid=True), ForeignKey("external_identities.id", ondelete="SET NULL"), nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String(30), nullable=True)
    last_error_code = Column(String(80), nullable=True)
    last_error_message = Column(Text, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
