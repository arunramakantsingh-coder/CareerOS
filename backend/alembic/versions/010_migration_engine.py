"""Add Migration Intelligence tables

Revision ID: 010_migration_engine
Revises: 009_remote_eligibility
Create Date: 2026-08-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = '010_migration_engine'
down_revision: Union[str, None] = '009_remote_eligibility'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Migration Intelligence tables."""
    
    # Create countries table
    op.create_table(
        'countries',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(2), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('region', sa.String(50), nullable=True),
        sa.Column('immigration_authority', sa.String(255), nullable=True),
        sa.Column('official_website', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('meta_data', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create visas table
    op.create_table(
        'visas',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('country_id', UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_visas_country_id', 'visas', 'countries', ['country_id'], ['id'])
    
    # Create migration_rules table
    op.create_table(
        'migration_rules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('visa_id', UUID(as_uuid=True), nullable=False),
        sa.Column('rule_key', sa.String(100), nullable=False),
        sa.Column('rule_type', sa.String(50), nullable=False),
        sa.Column('rule_value', sa.JSON, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('condition_text', sa.Text, nullable=True),
        sa.Column('effective_from', sa.DateTime, nullable=False),
        sa.Column('effective_to', sa.DateTime, nullable=True),
        sa.Column('is_current', sa.Boolean, server_default='true'),
        sa.Column('source_type', sa.String(50), nullable=True),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('source_reference', sa.String(255), nullable=True),
        sa.Column('verified_at', sa.DateTime, nullable=True),
        sa.Column('verified_by', sa.String(100), nullable=True),
        sa.Column('meta_data', sa.JSON, nullable=True),
        sa.Column('priority', sa.Integer, server_default='1'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_migration_rules_visa_id', 'migration_rules', 'visas', ['visa_id'], ['id'])
    
    # Create occupation_mappings table
    op.create_table(
        'occupation_mappings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('country_id', UUID(as_uuid=True), nullable=False),
        sa.Column('anzsc_code', sa.String(20), nullable=True),
        sa.Column('local_code', sa.String(20), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('skill_level', sa.Integer, nullable=True),
        sa.Column('skill_type', sa.String(50), nullable=True),
        sa.Column('is_in_demand', sa.Boolean, server_default='false'),
        sa.Column('is_sponsorship_eligible', sa.Boolean, server_default='false'),
        sa.Column('is_skills_assessment_required', sa.Boolean, server_default='true'),
        sa.Column('assessing_authority', sa.String(255), nullable=True),
        sa.Column('assessing_website', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_occupation_mappings_country_id', 'occupation_mappings', 'countries', ['country_id'], ['id'])
    
    # Create migration_pathways table
    op.create_table(
        'migration_pathways',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('visa_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('pathway_type', sa.String(50), nullable=False),
        sa.Column('requirements', sa.JSON, nullable=True),
        sa.Column('points_required', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('is_current', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_migration_pathways_visa_id', 'migration_pathways', 'visas', ['visa_id'], ['id'])
    
    # Create migration_profiles table
    op.create_table(
        'migration_profiles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('age', sa.Integer, nullable=True),
        sa.Column('nationality', sa.String(100), nullable=True),
        sa.Column('country_of_residence', sa.String(100), nullable=True),
        sa.Column('education_level', sa.String(50), nullable=True),
        sa.Column('field_of_study', sa.String(255), nullable=True),
        sa.Column('years_experience', sa.Integer, nullable=True),
        sa.Column('english_level', sa.String(20), nullable=True),
        sa.Column('english_test', sa.String(50), nullable=True),
        sa.Column('english_score', sa.JSON, nullable=True),
        sa.Column('occupation_title', sa.String(255), nullable=True),
        sa.Column('occupation_code', sa.String(20), nullable=True),
        sa.Column('target_countries', sa.JSON, nullable=True),
        sa.Column('target_visas', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_migration_profiles_user_id', 'migration_profiles', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    """Drop Migration Intelligence tables."""
    op.drop_table('migration_profiles')
    op.drop_table('migration_pathways')
    op.drop_table('occupation_mappings')
    op.drop_table('migration_rules')
    op.drop_table('visas')
    op.drop_table('countries')




