"""Add Remote Eligibility tables

Revision ID: 009_remote_eligibility
Revises: 008_semantic_discovery
Create Date: 2026-08-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = '009_remote_eligibility'
down_revision: Union[str, None] = '008_semantic_discovery'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Remote Eligibility tables."""
    
    # Add candidate location fields to users
    op.add_column('users', sa.Column('candidate_location', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('candidate_timezone', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('candidate_authorization', sa.JSON, nullable=True))
    
    # Create remote_eligibilities table
    op.create_table(
        'remote_eligibilities',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('remote_classification', sa.String(50), nullable=True),
        sa.Column('overall_remote_score', sa.Float, nullable=False),
        sa.Column('timezone_score', sa.Float, nullable=True),
        sa.Column('authorization_score', sa.Float, nullable=True),
        sa.Column('sponsorship_score', sa.Float, nullable=True),
        sa.Column('contractor_score', sa.Float, nullable=True),
        sa.Column('relocation_score', sa.Float, nullable=True),
        sa.Column('remote_analysis', sa.JSON, nullable=True),
        sa.Column('restrictions', sa.JSON, nullable=True),
        sa.Column('requirements', sa.JSON, nullable=True),
        sa.Column('is_remote_eligible', sa.Boolean, server_default='false'),
        sa.Column('is_timezone_compatible', sa.Boolean, server_default='false'),
        sa.Column('has_work_authorization', sa.Boolean, server_default='false'),
        sa.Column('requires_sponsorship', sa.Boolean, server_default='false'),
        sa.Column('requires_relocation', sa.Boolean, server_default='false'),
        sa.Column('allows_contractor', sa.Boolean, server_default='false'),
        sa.Column('allows_eor', sa.Boolean, server_default='false'),
        sa.Column('candidate_location', sa.String(255), nullable=True),
        sa.Column('candidate_timezone', sa.String(50), nullable=True),
        sa.Column('candidate_authorization', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_remote_eligibilities_user_id', 'remote_eligibilities', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_remote_eligibilities_job_id', 'remote_eligibilities', 'jobs', ['job_id'], ['id'])


def downgrade() -> None:
    """Drop Remote Eligibility tables."""
    op.drop_table('remote_eligibilities')
    op.drop_column('users', 'candidate_authorization')
    op.drop_column('users', 'candidate_timezone')
    op.drop_column('users', 'candidate_location')
