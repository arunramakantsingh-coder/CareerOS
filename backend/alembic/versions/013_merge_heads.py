"""Merge skill_gap and v01_product branches

Revision ID: 013_merge_heads
Revises: 012_skill_gap, 012_v01_product
Create Date: 2026-08-27

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '013_merge_heads'
down_revision: Union[str, Sequence[str], None] = ('012_skill_gap', '012_v01_product')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge two heads into one."""
    # This migration merges the branches; no schema changes needed
    pass


def downgrade() -> None:
    """Downgrade from merged state."""
    pass
