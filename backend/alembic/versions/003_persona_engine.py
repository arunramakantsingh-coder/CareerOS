"""Add Persona Engine tables

Revision ID: 003_persona_engine
Revises: 002_career_vault
Create Date: 2026-08-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = '003_persona_engine'
down_revision: Union[str, None] = '002_career_vault'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Persona Engine tables."""
    
    # Create personas table
    op.create_table(
        'personas',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('career_profile_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='false'),
        sa.Column('is_default', sa.Boolean, server_default='false'),
        sa.Column('target_titles', sa.JSON, nullable=True),
        sa.Column('target_industries', sa.JSON, nullable=True),
        sa.Column('target_locations', sa.JSON, nullable=True),
        sa.Column('target_companies', sa.JSON, nullable=True),
        sa.Column('preferred_seniority', sa.String(50), nullable=True),
        sa.Column('salary_preferences', sa.JSON, nullable=True),
        sa.Column('remote_preference', sa.String(20), nullable=True),
        sa.Column('migration_preference', sa.String(20), nullable=True),
        sa.Column('skill_weights', sa.JSON, nullable=True),
        sa.Column('capability_weights', sa.JSON, nullable=True),
        sa.Column('keywords', sa.JSON, nullable=True),
        sa.Column('positioning', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_personas_user_id', 'personas', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_personas_career_profile_id', 'personas', 'career_profiles', ['career_profile_id'], ['id'])
    
    # Create persona_skill_weights table
    op.create_table(
        'persona_skill_weights',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('persona_id', UUID(as_uuid=True), nullable=False),
        sa.Column('skill_id', UUID(as_uuid=True), nullable=False),
        sa.Column('weight', sa.Float, server_default='1.0'),
        sa.Column('importance', sa.Integer, server_default='1'),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_persona_skill_weights_persona_id', 'persona_skill_weights', 'personas', ['persona_id'], ['id'])
    op.create_foreign_key('fk_persona_skill_weights_skill_id', 'persona_skill_weights', 'skills', ['skill_id'], ['id'])
    
    # Create unique constraint for persona_id + skill_id
    op.create_unique_constraint('uq_persona_skill_weights_persona_skill', 'persona_skill_weights', ['persona_id', 'skill_id'])


def downgrade() -> None:
    """Drop Persona Engine tables."""
    op.drop_constraint('uq_persona_skill_weights_persona_skill', 'persona_skill_weights')
    op.drop_table('persona_skill_weights')
    op.drop_table('personas')
