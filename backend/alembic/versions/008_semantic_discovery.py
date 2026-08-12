"""Add Semantic Job Discovery tables

Revision ID: 008_semantic_discovery
Revises: 007_job_source_connector
Create Date: 2026-08-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = '008_semantic_discovery'
down_revision: Union[str, None] = '007_job_source_connector'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Semantic Discovery tables."""
    
    # Create job_discoveries table
    op.create_table(
        'job_discoveries',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('overall_score', sa.Float, nullable=False),
        sa.Column('title_match', sa.Float, nullable=True),
        sa.Column('capability_match', sa.Float, nullable=True),
        sa.Column('skill_match', sa.Float, nullable=True),
        sa.Column('responsibility_match', sa.Float, nullable=True),
        sa.Column('career_match', sa.Float, nullable=True),
        sa.Column('capability_details', sa.JSON, nullable=True),
        sa.Column('skill_details', sa.JSON, nullable=True),
        sa.Column('responsibility_details', sa.JSON, nullable=True),
        sa.Column('career_details', sa.JSON, nullable=True),
        sa.Column('discovery_rank', sa.Integer, nullable=True),
        sa.Column('discovery_confidence', sa.Float, nullable=True),
        sa.Column('matched_capabilities', sa.JSON, nullable=True),
        sa.Column('missing_capabilities', sa.JSON, nullable=True),
        sa.Column('is_viewed', sa.Boolean, server_default='false'),
        sa.Column('is_saved', sa.Boolean, server_default='false'),
        sa.Column('is_applied', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_job_discoveries_user_id', 'job_discoveries', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_job_discoveries_job_id', 'job_discoveries', 'jobs', ['job_id'], ['id'])


def downgrade() -> None:
    """Drop Semantic Discovery tables."""
    op.drop_table('job_discoveries')
