"""Add Match Engine tables

Revision ID: 005_match_engine
Revises: 004_job_intelligence
Create Date: 2026-08-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = '005_match_engine'
down_revision: Union[str, None] = '004_job_intelligence'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Match Engine tables."""
    
    # Create matches table
    op.create_table(
        'matches',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('persona_id', UUID(as_uuid=True), nullable=False),
        sa.Column('overall_score', sa.Float, nullable=False),
        sa.Column('dimension_scores', sa.JSON, nullable=False),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('recommendation', sa.Text, nullable=True),
        sa.Column('matched_skills', sa.JSON, nullable=True),
        sa.Column('partial_skills', sa.JSON, nullable=True),
        sa.Column('missing_skills', sa.JSON, nullable=True),
        sa.Column('hard_failures', sa.JSON, nullable=True),
        sa.Column('gaps', sa.JSON, nullable=True),
        sa.Column('risks', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_matches_user_id', 'matches', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_matches_job_id', 'matches', 'jobs', ['job_id'], ['id'])
    op.create_foreign_key('fk_matches_persona_id', 'matches', 'personas', ['persona_id'], ['id'])
    
    # Create match_dimensions table
    op.create_table(
        'match_dimensions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('match_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('score', sa.Float, nullable=False),
        sa.Column('weight', sa.Float, nullable=False),
        sa.Column('matched_items', sa.JSON, nullable=True),
        sa.Column('partial_items', sa.JSON, nullable=True),
        sa.Column('missing_items', sa.JSON, nullable=True),
        sa.Column('explanation', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_match_dimensions_match_id', 'match_dimensions', 'matches', ['match_id'], ['id'])
    
    # Create match_recommendations table
    op.create_table(
        'match_recommendations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('match_id', UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('priority', sa.String(20), nullable=True),
        sa.Column('recommendation', sa.Text, nullable=False),
        sa.Column('action_required', sa.String(500), nullable=True),
        sa.Column('impact', sa.String(20), nullable=True),
        sa.Column('difficulty', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_match_recommendations_match_id', 'match_recommendations', 'matches', ['match_id'], ['id'])


def downgrade() -> None:
    """Drop Match Engine tables."""
    op.drop_table('match_recommendations')
    op.drop_table('match_dimensions')
    op.drop_table('matches')
