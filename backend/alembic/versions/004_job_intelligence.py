"""Add Job Intelligence tables

Revision ID: 004_job_intelligence
Revises: 003_persona_engine
Create Date: 2026-08-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = '004_job_intelligence'
down_revision: Union[str, None] = '003_persona_engine'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Job Intelligence tables."""
    
    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('source_id', sa.String(255), nullable=True),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('source_name', sa.String(100), nullable=True),
        sa.Column('raw_jd', sa.Text, nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('company', sa.String(255), nullable=True),
        sa.Column('company_description', sa.Text, nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('remote_policy', sa.String(50), nullable=True),
        sa.Column('salary_min', sa.Float, nullable=True),
        sa.Column('salary_max', sa.Float, nullable=True),
        sa.Column('salary_currency', sa.String(3), nullable=True),
        sa.Column('salary_period', sa.String(20), nullable=True),
        sa.Column('is_processed', sa.Boolean, server_default='false'),
        sa.Column('processed_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_jobs_user_id', 'jobs', 'users', ['user_id'], ['id'])
    
    # Create job_dna table
    op.create_table(
        'job_dna',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('role_family', sa.String(100), nullable=True),
        sa.Column('seniority', sa.String(50), nullable=True),
        sa.Column('capabilities', sa.JSON, nullable=True),
        sa.Column('skills', sa.JSON, nullable=True),
        sa.Column('mandatory_skills', sa.JSON, nullable=True),
        sa.Column('preferred_skills', sa.JSON, nullable=True),
        sa.Column('technologies', sa.JSON, nullable=True),
        sa.Column('experience_requirements', sa.JSON, nullable=True),
        sa.Column('architecture_domains', sa.JSON, nullable=True),
        sa.Column('leadership_scope', sa.JSON, nullable=True),
        sa.Column('governance_requirements', sa.JSON, nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('industry_context', sa.Text, nullable=True),
        sa.Column('location', sa.JSON, nullable=True),
        sa.Column('mobility_requirements', sa.JSON, nullable=True),
        sa.Column('education_requirements', sa.JSON, nullable=True),
        sa.Column('certifications_required', sa.JSON, nullable=True),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('keywords', sa.JSON, nullable=True),
        sa.Column('embedding', sa.JSON, nullable=True),
        sa.Column('confidence_score', sa.Float, nullable=True),
        sa.Column('completeness_score', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_job_dna_job_id', 'job_dna', 'jobs', ['job_id'], ['id'])
    op.create_unique_constraint('uq_job_dna_job_id', 'job_dna', ['job_id'])
    
    # Create job_skills table
    op.create_table(
        'job_skills',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('skill_name', sa.String(100), nullable=False),
        sa.Column('skill_category', sa.String(50), nullable=True),
        sa.Column('is_mandatory', sa.Boolean, server_default='false'),
        sa.Column('is_preferred', sa.Boolean, server_default='false'),
        sa.Column('proficiency_required', sa.String(20), nullable=True),
        sa.Column('years_required', sa.Float, nullable=True),
        sa.Column('context', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_job_skills_job_id', 'job_skills', 'jobs', ['job_id'], ['id'])
    
    # Create job_responsibilities table
    op.create_table(
        'job_responsibilities',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('order', sa.Integer, nullable=True),
        sa.Column('is_primary', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_job_responsibilities_job_id', 'job_responsibilities', 'jobs', ['job_id'], ['id'])
    
    # Create capability_taxonomy table
    op.create_table(
        'capability_taxonomy',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('parent_id', UUID(as_uuid=True), nullable=True),
        sa.Column('synonyms', sa.JSON, nullable=True),
        sa.Column('keywords', sa.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('importance', sa.Integer, server_default='1'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_capability_taxonomy_parent_id', 'capability_taxonomy', 'capability_taxonomy', ['parent_id'], ['id'])


def downgrade() -> None:
    """Drop Job Intelligence tables."""
    op.drop_table('capability_taxonomy')
    op.drop_table('job_responsibilities')
    op.drop_table('job_skills')
    op.drop_table('job_dna')
    op.drop_table('jobs')
