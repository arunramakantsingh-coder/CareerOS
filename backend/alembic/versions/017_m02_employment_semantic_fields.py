"""Add semantic employment fields for AI reconciliation.

Revision ID: 017_m02_employment_semantic_fields
Revises: 016_m02_identity_intelligence
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "017_m02_employment_semantic_fields"
down_revision: Union[str, None] = "016_m02_identity_intelligence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table in inspector.get_table_names() and column in {
        item["name"] for item in inspector.get_columns(table)
    }


def _add_column(table: str, column: sa.Column) -> None:
    if not _has_column(table, column.name):
        op.add_column(table, column)


def upgrade() -> None:
    _add_column("professional_experiences", sa.Column("client", sa.String(255), nullable=True))
    _add_column("professional_experiences", sa.Column("technologies", sa.JSON(), nullable=True))
    _add_column("professional_experiences", sa.Column("industries", sa.JSON(), nullable=True))


def downgrade() -> None:
    for column in ("industries", "technologies", "client"):
        if _has_column("professional_experiences", column):
            op.drop_column("professional_experiences", column)
