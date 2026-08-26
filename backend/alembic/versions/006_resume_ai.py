"""Add Resume AI tables

Revision ID: 006_resume_ai
Revises: 005_match_engine
Create Date: 2026-08-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = '006_resume_ai'
down_revision: Union[str, None] = '005_match_engine'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Resume AI tables."""
    
    # Create resume_versions table
    op.create_table(
        'resume_versions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('persona_id', UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.Integer, nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('is_preview', sa.Boolean, server_default='false'),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('format_type', sa.String(20), server_default='ats'),
        sa.Column('ats_score', sa.Float, nullable=True),
        sa.Column('keyword_coverage', sa.Float, nullable=True),
        sa.Column('generation_notes', sa.Text, nullable=True),
        sa.Column('truth_score', sa.Float, nullable=True),
        sa.Column('status', sa.String(20), server_default='draft'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_resume_versions_user_id', 'resume_versions', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_resume_versions_job_id', 'resume_versions', 'jobs', ['job_id'], ['id'])
    op.create_foreign_key('fk_resume_versions_persona_id', 'resume_versions', 'personas', ['persona_id'], ['id'])
    
    # Create resume_sections table
    op.create_table(
        'resume_sections',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('resume_id', UUID(as_uuid=True), nullable=False),
        sa.Column('section_type', sa.String(50), nullable=False),
        sa.Column('section_title', sa.String(100), nullable=True),
        sa.Column('order', sa.Integer, nullable=False, server_default='0'),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('source_evidence', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_resume_sections_resume_id', 'resume_sections', 'resume_versions', ['resume_id'], ['id'])
    
    # Create resume_evidence_links table
    op.create_table(
        'resume_evidence_links',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('section_id', UUID(as_uuid=True), nullable=False),
        sa.Column('statement', sa.Text, nullable=False),
        sa.Column('evidence_id', UUID(as_uuid=True), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=True),
        sa.Column('source_reference', sa.JSON, nullable=True),
        sa.Column('is_verified', sa.Boolean, server_default='false'),
        sa.Column('confidence', sa.Float, server_default='1.0'),
        sa.Column('explanation', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_resume_evidence_links_section_id', 'resume_evidence_links', 'resume_sections', ['section_id'], ['id'])
    op.create_foreign_key('fk_resume_evidence_links_evidence_id', 'resume_evidence_links', 'career_evidence', ['evidence_id'], ['id'])


def downgrade() -> None:
    """Drop Resume AI tables."""
    op.drop_table('resume_evidence_links')
    op.drop_table('resume_sections')
    op.drop_table('resume_versions')
