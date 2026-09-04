"""M02 professional identity intelligence foundation.

Revision ID: 016_m02_identity_intelligence
Revises: 015_document_vault_enhancement
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "016_m02_identity_intelligence"
down_revision: Union[str, None] = "015_document_vault_enhancement"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(30), nullable=False, server_default="user"))
    op.create_index("idx_users_role", "users", ["role"])

    op.add_column("documents", sa.Column("user_label", sa.String(255), nullable=True))
    op.add_column("documents", sa.Column("detected_type", sa.String(80), nullable=True))
    op.add_column("documents", sa.Column("classification_reason", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("verification_status", sa.String(30), nullable=False, server_default="reported"))
    op.add_column("documents", sa.Column("processing_stage", sa.String(40), nullable=False, server_default="uploaded"))
    op.create_index("idx_documents_detected_type", "documents", ["candidate_id", "detected_type"])
    op.create_index("idx_documents_verification_status", "documents", ["candidate_id", "verification_status"])

    op.create_table(
        "career_fact_evidence",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("candidate_id", UUID(as_uuid=True), sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fact_type", sa.String(50), nullable=False),
        sa.Column("fact_id", UUID(as_uuid=True), nullable=False),
        sa.Column("relationship", sa.String(40), nullable=False, server_default="supports"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.7"),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_fact_evidence_fact", "career_fact_evidence", ["candidate_id", "fact_type", "fact_id"])
    op.create_index("idx_fact_evidence_document", "career_fact_evidence", ["document_id"])

    op.create_table(
        "persona_suggestions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("candidate_id", UUID(as_uuid=True), sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role_family", sa.String(120), nullable=True),
        sa.Column("positioning", sa.Text(), nullable=True),
        sa.Column("target_titles", sa.JSON(), nullable=True),
        sa.Column("supporting_fact_ids", sa.JSON(), nullable=True),
        sa.Column("supporting_document_ids", sa.JSON(), nullable=True),
        sa.Column("missing_evidence", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="suggested"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_persona_suggestions_user", "persona_suggestions", ["user_id", "status"])

    op.create_table(
        "email_connector_accounts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("email_address", sa.String(320), nullable=True),
        sa.Column("auth_method", sa.String(30), nullable=False, server_default="oauth2"),
        sa.Column("status", sa.String(30), nullable=False, server_default="available"),
        sa.Column("capabilities", sa.JSON(), nullable=True),
        sa.Column("scopes", sa.JSON(), nullable=True),
        sa.Column("external_identity_id", UUID(as_uuid=True), sa.ForeignKey("external_identities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(), nullable=True),
        sa.Column("last_sync_at", sa.DateTime(), nullable=True),
        sa.Column("last_sync_status", sa.String(30), nullable=True),
        sa.Column("last_error_code", sa.String(80), nullable=True),
        sa.Column("last_error_message", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_email_connector_user_provider", "email_connector_accounts", ["user_id", "provider"])


def downgrade() -> None:
    op.drop_index("idx_email_connector_user_provider", table_name="email_connector_accounts")
    op.drop_table("email_connector_accounts")
    op.drop_index("idx_persona_suggestions_user", table_name="persona_suggestions")
    op.drop_table("persona_suggestions")
    op.drop_index("idx_fact_evidence_document", table_name="career_fact_evidence")
    op.drop_index("idx_fact_evidence_fact", table_name="career_fact_evidence")
    op.drop_table("career_fact_evidence")
    op.drop_index("idx_documents_verification_status", table_name="documents")
    op.drop_index("idx_documents_detected_type", table_name="documents")
    op.drop_column("documents", "processing_stage")
    op.drop_column("documents", "verification_status")
    op.drop_column("documents", "classification_reason")
    op.drop_column("documents", "detected_type")
    op.drop_column("documents", "user_label")
    op.drop_index("idx_users_role", table_name="users")
    op.drop_column("users", "role")
