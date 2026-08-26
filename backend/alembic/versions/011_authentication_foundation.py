"""Add authentication foundation
Revision ID: 011_authentication_foundation
Revises: 010_migration_engine
Create Date: 2026-08-24
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
revision: str = "011_authentication_foundation"
down_revision: Union[str, None] = "010_migration_engine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(255), nullable=True))
def downgrade() -> None:
    op.drop_column("users", "password_hash")
