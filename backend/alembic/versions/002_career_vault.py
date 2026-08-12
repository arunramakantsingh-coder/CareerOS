"""Add Career Vault tables

Revision ID: 002_career_vault
Revises: 001_initial_schema
Create Date: 2026-08-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = '002_career_vault'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Career Vault tables."""
    
    # Create career_profiles table
    op.create_table(
        'career_profiles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('target_roles', sa.JSON, nullable=True),
        sa.Column('seniority', sa.String(50), nullable=True),
        sa.Column('years_experience', sa.Integer, nullable=True),
        sa.Column('preferred_locations', sa.JSON, nullable=True),
        sa.Column('remote_preference', sa.String(20), nullable=True),
        sa.Column('salary_preferences', sa.JSON, nullable=True),
        sa.Column('industries', sa.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_career_profiles_user_id', 'career_profiles', 'users', ['user_id'], ['id'])
    
    # Create employments table
    op.create_table(
        'employments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('career_profile_id', UUID(as_uuid=True), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('start_date', sa.DateTime, nullable=False),
        sa.Column('end_date', sa.DateTime, nullable=True),
        sa.Column('is_current', sa.Boolean, server_default='false'),
        sa.Column('responsibilities', sa.Text, nullable=True),
        sa.Column('achievements', sa.JSON, nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('company_size', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_employments_career_profile_id', 'employments', 'career_profiles', ['career_profile_id'], ['id'])
    
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('career_profile_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('role', sa.String(255), nullable=True),
        sa.Column('technologies', sa.JSON, nullable=True),
        sa.Column('responsibilities', sa.JSON, nullable=True),
        sa.Column('achievements', sa.JSON, nullable=True),
        sa.Column('start_date', sa.DateTime, nullable=True),
        sa.Column('end_date', sa.DateTime, nullable=True),
        sa.Column('is_current', sa.Boolean, server_default='false'),
        sa.Column('client', sa.String(255), nullable=True),
        sa.Column('team_size', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_projects_career_profile_id', 'projects', 'career_profiles', ['career_profile_id'], ['id'])
    
    # Create skills table
    op.create_table(
        'skills',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('career_profile_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('proficiency', sa.String(20), nullable=True),
        sa.Column('years_experience', sa.Float, nullable=True),
        sa.Column('last_used', sa.String(10), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_core', sa.String(10), server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_skills_career_profile_id', 'skills', 'career_profiles', ['career_profile_id'], ['id'])
    
    # Create certifications table
    op.create_table(
        'certifications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('career_profile_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('issuer', sa.String(255), nullable=False),
        sa.Column('issue_date', sa.DateTime, nullable=True),
        sa.Column('expiry_date', sa.DateTime, nullable=True),
        sa.Column('credential_reference', sa.String(255), nullable=True),
        sa.Column('credential_url', sa.String(500), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_active', sa.String(10), server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_certifications_career_profile_id', 'certifications', 'career_profiles', ['career_profile_id'], ['id'])
    
    # Create educations table
    op.create_table(
        'educations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('career_profile_id', UUID(as_uuid=True), nullable=False),
        sa.Column('institution', sa.String(255), nullable=False),
        sa.Column('degree', sa.String(255), nullable=False),
        sa.Column('field_of_study', sa.String(255), nullable=True),
        sa.Column('start_date', sa.DateTime, nullable=True),
        sa.Column('end_date', sa.DateTime, nullable=True),
        sa.Column('is_current', sa.String(10), server_default='false'),
        sa.Column('grade', sa.String(50), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('achievements', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_educations_career_profile_id', 'educations', 'career_profiles', ['career_profile_id'], ['id'])
    
    # Create achievements table
    op.create_table(
        'achievements',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('career_profile_id', UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('date', sa.DateTime, nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('metrics', sa.JSON, nullable=True),
        sa.Column('context', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_achievements_career_profile_id', 'achievements', 'career_profiles', ['career_profile_id'], ['id'])
    
    # Create technologies table
    op.create_table(
        'technologies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('career_profile_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('vendor', sa.String(100), nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('proficiency', sa.String(20), nullable=True),
        sa.Column('years_experience', sa.Float, nullable=True),
        sa.Column('last_used', sa.String(10), nullable=True),
        sa.Column('certifications', sa.JSON, nullable=True),
        sa.Column('projects_used', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_technologies_career_profile_id', 'technologies', 'career_profiles', ['career_profile_id'], ['id'])
    
    # Create career_evidence table
    op.create_table(
        'career_evidence',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('career_profile_id', UUID(as_uuid=True), nullable=False),
        sa.Column('claim', sa.Text, nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('source_id', UUID(as_uuid=True), nullable=True),
        sa.Column('source_entity', sa.String(50), nullable=True),
        sa.Column('source_file', sa.String(500), nullable=True),
        sa.Column('excerpt', sa.Text, nullable=True),
        sa.Column('confidence', sa.Float, server_default='1.0'),
        sa.Column('verified_at', sa.DateTime, nullable=True),
        sa.Column('verified_by', sa.String(100), nullable=True),
        sa.Column('metadata', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_career_evidence_career_profile_id', 'career_evidence', 'career_profiles', ['career_profile_id'], ['id'])
    
    # Create career_preferences table
    op.create_table(
        'career_preferences',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('work_mode', sa.String(20), nullable=True),
        sa.Column('preferred_locations', sa.JSON, nullable=True),
        sa.Column('preferred_countries', sa.JSON, nullable=True),
        sa.Column('target_industries', sa.JSON, nullable=True),
        sa.Column('target_role_families', sa.JSON, nullable=True),
        sa.Column('salary_expectations', sa.JSON, nullable=True),
        sa.Column('open_to_relocation', sa.String(10), server_default='false'),
        sa.Column('open_to_international', sa.String(10), server_default='false'),
        sa.Column('willing_to_travel', sa.String(10), server_default='false'),
        sa.Column('travel_percentage', sa.Integer, nullable=True),
        sa.Column('visa_status', sa.String(50), nullable=True),
        sa.Column('work_authorization', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_career_preferences_user_id', 'career_preferences', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    """Drop Career Vault tables."""
    op.drop_table('career_preferences')
    op.drop_table('career_evidence')
    op.drop_table('technologies')
    op.drop_table('achievements')
    op.drop_table('educations')
    op.drop_table('certifications')
    op.drop_table('skills')
    op.drop_table('projects')
    op.drop_table('employments')
    op.drop_table('career_profiles')
