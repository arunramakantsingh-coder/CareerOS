"""Update Document model with additional fields

Revision ID: 015_document_vault_enhancement
Revises: 014_m02_identity_career_intake
Create Date: 2026-08-29

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = '015_document_vault_enhancement'
down_revision: Union[str, None] = '014_m02_identity_career_intake'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add document model fields."""
    
    # Add new columns to documents table
    op.add_column('documents', sa.Column('content_hash', sa.String(64), nullable=True))
    op.add_column('documents', sa.Column('issuer', sa.String(255), nullable=True))
    op.add_column('documents', sa.Column('issue_date', sa.DateTime, nullable=True))
    op.add_column('documents', sa.Column('expiry_date', sa.DateTime, nullable=True))
    op.add_column('documents', sa.Column('document_number', sa.String(255), nullable=True))
    op.add_column('documents', sa.Column('document_type', sa.String(50), nullable=True))
    op.add_column('documents', sa.Column('batch_id', UUID(as_uuid=True), nullable=True))
    op.add_column('documents', sa.Column('is_zip_content', sa.Boolean, server_default='false'))
    op.add_column('documents', sa.Column('parent_zip_id', UUID(as_uuid=True), nullable=True))
    op.add_column('documents', sa.Column('classification_confidence', sa.Float, nullable=True))
    
    # Add index for content_hash
    op.create_index('idx_documents_content_hash', 'documents', ['content_hash'])


def downgrade() -> None:
    """Remove document model fields."""
    op.drop_index('idx_documents_content_hash', table_name='documents')
    op.drop_column('documents', 'classification_confidence')
    op.drop_column('documents', 'parent_zip_id')
    op.drop_column('documents', 'is_zip_content')
    op.drop_column('documents', 'batch_id')
    op.drop_column('documents', 'document_type')
    op.drop_column('documents', 'document_number')
    op.drop_column('documents', 'expiry_date')
    op.drop_column('documents', 'issue_date')
    op.drop_column('documents', 'issuer')
    op.drop_column('documents', 'content_hash')
