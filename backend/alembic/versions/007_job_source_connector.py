"""Add Job Source Connector tables

Revision ID: 007_job_source_connector
Revises: 006_resume_ai
Create Date: 2026-08-12

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = '007_job_source_connector'
down_revision: Union[str, None] = '006_resume_ai'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Job Source Connector tables."""
    
    # Create job_sources table
    op.create_table(
        'job_sources',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('config', sa.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('is_system', sa.Boolean, server_default='false'),
        sa.Column('last_sync', sa.DateTime, nullable=True),
        sa.Column('sync_status', sa.String(20), nullable=True),
        sa.Column('total_listings', sa.Integer, server_default='0'),
        sa.Column('error_count', sa.Integer, server_default='0'),
        sa.Column('last_error', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_job_sources_user_id', 'job_sources', 'users', ['user_id'], ['id'])
    
    # Create job_source_connections table
    op.create_table(
        'job_source_connections',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('source_id', UUID(as_uuid=True), nullable=False),
        sa.Column('connection_type', sa.String(50), nullable=False),
        sa.Column('credentials', sa.Text, nullable=True),
        sa.Column('endpoint', sa.String(500), nullable=True),
        sa.Column('headers', sa.JSON, nullable=True),
        sa.Column('is_valid', sa.Boolean, server_default='false'),
        sa.Column('last_used', sa.DateTime, nullable=True),
        sa.Column('expires_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_job_source_connections_source_id', 'job_source_connections', 'job_sources', ['source_id'], ['id'])
    
    # Create job_listings table
    op.create_table(
        'job_listings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('source_id', UUID(as_uuid=True), nullable=True),
        sa.Column('external_id', sa.String(255), nullable=True),
        sa.Column('external_url', sa.String(500), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('parsed_title', sa.String(255), nullable=True),
        sa.Column('parsed_company', sa.String(255), nullable=True),
        sa.Column('parsed_location', sa.String(255), nullable=True),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('is_duplicate', sa.Boolean, server_default='false'),
        sa.Column('duplicate_of', UUID(as_uuid=True), nullable=True),
        sa.Column('posted_at', sa.DateTime, nullable=True),
        sa.Column('last_seen_at', sa.DateTime, nullable=True),
        sa.Column('ingested_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('source_metadata', sa.JSON, nullable=True),
        sa.Column('fingerprint', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_job_listings_user_id', 'job_listings', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_job_listings_source_id', 'job_listings', 'job_sources', ['source_id'], ['id'])


def downgrade() -> None:
    """Drop Job Source Connector tables."""
    op.drop_table('job_listings')
    op.drop_table('job_source_connections')
    op.drop_table('job_sources')
