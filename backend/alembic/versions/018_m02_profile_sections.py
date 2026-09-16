"""Add canonical profile project and accomplishment sections.

Revision ID: 018_m02_profile_sections
Revises: 017_m02_employment_semantic_fields
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "018_m02_profile_sections"
down_revision: Union[str, None] = "017_m02_employment_semantic_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table in inspector.get_table_names() and column in {
        item["name"] for item in inspector.get_columns(table)
    }


def upgrade() -> None:
    if not _has_column("candidate_profiles", "projects"):
        op.add_column("candidate_profiles", sa.Column("projects", sa.JSON(), nullable=True))
    if not _has_column("candidate_profiles", "accomplishments"):
        op.add_column("candidate_profiles", sa.Column("accomplishments", sa.JSON(), nullable=True))


def downgrade() -> None:
    if _has_column("candidate_profiles", "accomplishments"):
        op.drop_column("candidate_profiles", "accomplishments")
    if _has_column("candidate_profiles", "projects"):
        op.drop_column("candidate_profiles", "projects")
