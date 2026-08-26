"""Add password_hash to users

Revision ID: 011_password_hash
Revises: 010_migration_engine
Create Date: 2026-08-26

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '011_password_hash'
down_revision: Union[str, None] = '010_migration_engine'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add password_hash column to users."""
    op.add_column('users', sa.Column('password_hash', sa.String(255), nullable=True))


def downgrade() -> None:
    """Remove password_hash column from users."""
    op.drop_column('users', 'password_hash')
