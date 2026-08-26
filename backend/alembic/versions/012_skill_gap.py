"""Add SkillGapObservation and SkillGapAggregate tables

Revision ID: 012_skill_gap
Revises: 011_password_hash
Create Date: 2026-08-26

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = '012_skill_gap'
down_revision: Union[str, None] = '011_password_hash'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create skill gap tables."""
    
    # Create skill_gap_observations table
    op.create_table(
        'skill_gap_observations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('skill_name', sa.String(255), nullable=False),
        sa.Column('skill_category', sa.String(50), nullable=True),
        sa.Column('gap_type', sa.String(50), nullable=False),
        sa.Column('job_analysis_id', UUID(as_uuid=True), nullable=True),
        sa.Column('context', sa.JSON, nullable=True),
        sa.Column('is_recurring', sa.Boolean, server_default='false'),
        sa.Column('recurrence_count', sa.Integer, server_default='1'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_skill_gap_observations_user_id', 'skill_gap_observations', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_skill_gap_observations_job_id', 'skill_gap_observations', 'jobs', ['job_id'], ['id'])
    op.create_index('idx_skill_gap_observations_user_skill', 'skill_gap_observations', ['user_id', 'skill_name'])
    
    # Create skill_gap_aggregates table
    op.create_table(
        'skill_gap_aggregates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('skill_name', sa.String(255), nullable=False),
        sa.Column('skill_category', sa.String(50), nullable=True),
        sa.Column('occurrence_count', sa.Integer, server_default='0'),
        sa.Column('job_count', sa.Integer, server_default='0'),
        sa.Column('first_seen', sa.DateTime, nullable=True),
        sa.Column('last_seen', sa.DateTime, nullable=True),
        sa.Column('primary_gap_type', sa.String(50), nullable=True),
        sa.Column('is_critical', sa.Boolean, server_default='false'),
        sa.Column('context_summary', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_skill_gap_aggregates_user_id', 'skill_gap_aggregates', 'users', ['user_id'], ['id'])
    op.create_unique_constraint('uq_skill_gap_aggregates_user_skill', 'skill_gap_aggregates', ['user_id', 'skill_name'])
    op.create_index('idx_skill_gap_aggregates_user_skill', 'skill_gap_aggregates', ['user_id', 'skill_name'])


def downgrade() -> None:
    """Drop skill gap tables."""
    op.drop_table('skill_gap_aggregates')
    op.drop_table('skill_gap_observations')
