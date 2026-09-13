"""Create the global CareerOS Intelligence provider registry.

Revision ID: 019_global_intelligence_provider_registry
Revises: 018_m02_profile_sections
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "019_global_intelligence_provider_registry"
down_revision: Union[str, None] = "018_m02_profile_sections"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if _has_table("intelligence_provider_configs"):
        return

    op.create_table(
        "intelligence_provider_configs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("provider", sa.String(50), nullable=False, unique=True),
        sa.Column("label", sa.String(120), nullable=False),
        sa.Column("category", sa.String(30), nullable=False, server_default="cloud"),
        sa.Column("model", sa.String(255), nullable=True),
        sa.Column("base_url", sa.String(500), nullable=True),
        sa.Column("encrypted_api_key", sa.Text(), nullable=True),
        sa.Column("api_key_last4", sa.String(8), nullable=True),
        sa.Column("configured", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("capabilities", sa.JSON(), nullable=True),
        sa.Column("routing_policy", sa.JSON(), nullable=True),
        sa.Column("last_tested_at", sa.String(40), nullable=True),
        sa.Column("last_test_status", sa.String(30), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("idx_intelligence_provider_active", "intelligence_provider_configs", ["active"])


def downgrade() -> None:
    if _has_table("intelligence_provider_configs"):
        op.drop_index("idx_intelligence_provider_active", table_name="intelligence_provider_configs")
        op.drop_table("intelligence_provider_configs")
