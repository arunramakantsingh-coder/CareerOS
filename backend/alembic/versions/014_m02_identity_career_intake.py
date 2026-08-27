"""Add M02 Identity & Career Intake tables

Revision ID: 014_m02_identity_career_intake
Revises: 013_merge_heads
Create Date: 2026-08-27

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = '014_m02_identity_career_intake'
down_revision: Union[str, None] = '013_merge_heads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create M02 Identity & Career Intake tables."""
    
    # 1. Create external_identities table
    op.create_table(
        'external_identities',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('provider_user_id', sa.String(255), nullable=False),
        sa.Column('provider_email', sa.String(255), nullable=True),
        sa.Column('access_token', sa.Text, nullable=True),
        sa.Column('refresh_token', sa.Text, nullable=True),
        sa.Column('token_expires_at', sa.DateTime, nullable=True),
        sa.Column('provider_data', sa.JSON, nullable=True),
        sa.Column('scopes', sa.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('last_used', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_external_identities_user_id', 'external_identities', 'users', ['user_id'], ['id'])
    op.create_index('idx_external_identities_provider', 'external_identities', ['provider', 'provider_user_id'])
    
    # 2. Create candidate_profiles table
    op.create_table(
        'candidate_profiles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('linkedin_url', sa.String(500), nullable=True),
        sa.Column('linkedin_username', sa.String(255), nullable=True),
        sa.Column('primary_email', sa.String(255), nullable=True),
        sa.Column('primary_phone', sa.String(50), nullable=True),
        sa.Column('work_preferences', sa.JSON, nullable=True),
        sa.Column('years_experience', sa.Float, nullable=True),
        sa.Column('industries', sa.JSON, nullable=True),
        sa.Column('seniority', sa.String(50), nullable=True),
        sa.Column('completeness_score', sa.Float, nullable=True),
        sa.Column('completeness_breakdown', sa.JSON, nullable=True),
        sa.Column('reconciliation_status', sa.String(20), server_default='pending'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_candidate_profiles_user_id', 'candidate_profiles', 'users', ['user_id'], ['id'])
    op.create_index('idx_candidate_profiles_user_id', 'candidate_profiles', ['user_id'])
    
    # 3. Create professional_experiences table
    op.create_table(
        'professional_experiences',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('candidate_id', UUID(as_uuid=True), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('start_date', sa.DateTime, nullable=True),
        sa.Column('end_date', sa.DateTime, nullable=True),
        sa.Column('is_current', sa.Boolean, server_default='false'),
        sa.Column('responsibilities', sa.JSON, nullable=True),
        sa.Column('achievements', sa.JSON, nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('company_size', sa.String(50), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=True),
        sa.Column('source_id', UUID(as_uuid=True), nullable=True),
        sa.Column('is_reconciled', sa.Boolean, server_default='false'),
        sa.Column('reconciliation_status', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_professional_experiences_candidate_id', 'professional_experiences', 'candidate_profiles', ['candidate_id'], ['id'])
    
    # 4. Create candidate_skills table
    op.create_table(
        'candidate_skills',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('candidate_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('proficiency', sa.String(20), nullable=True),
        sa.Column('years_experience', sa.Float, nullable=True),
        sa.Column('last_used', sa.String(10), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=True),
        sa.Column('source_id', UUID(as_uuid=True), nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_candidate_skills_candidate_id', 'candidate_skills', 'candidate_profiles', ['candidate_id'], ['id'])
    op.create_index('idx_candidate_skills_name', 'candidate_skills', ['name'])
    
    # 5. Create candidate_certifications table
    op.create_table(
        'candidate_certifications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('candidate_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('issuer', sa.String(255), nullable=False),
        sa.Column('issue_date', sa.DateTime, nullable=True),
        sa.Column('expiry_date', sa.DateTime, nullable=True),
        sa.Column('credential_reference', sa.String(255), nullable=True),
        sa.Column('credential_url', sa.String(500), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=True),
        sa.Column('source_id', UUID(as_uuid=True), nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_candidate_certifications_candidate_id', 'candidate_certifications', 'candidate_profiles', ['candidate_id'], ['id'])
    
    # 6. Create candidate_educations table
    op.create_table(
        'candidate_educations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('candidate_id', UUID(as_uuid=True), nullable=False),
        sa.Column('institution', sa.String(255), nullable=False),
        sa.Column('degree', sa.String(255), nullable=False),
        sa.Column('field_of_study', sa.String(255), nullable=True),
        sa.Column('start_date', sa.DateTime, nullable=True),
        sa.Column('end_date', sa.DateTime, nullable=True),
        sa.Column('is_current', sa.Boolean, server_default='false'),
        sa.Column('grade', sa.String(50), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=True),
        sa.Column('source_id', UUID(as_uuid=True), nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_candidate_educations_candidate_id', 'candidate_educations', 'candidate_profiles', ['candidate_id'], ['id'])
    
    # 7. Create documents table
    op.create_table(
        'documents',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('candidate_id', UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=True),
        sa.Column('file_type', sa.String(50), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('storage_path', sa.String(500), nullable=False),
        sa.Column('storage_url', sa.String(500), nullable=True),
        sa.Column('document_category', sa.String(50), nullable=True),
        sa.Column('document_subcategory', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), server_default='uploaded'),
        sa.Column('processing_status', sa.JSON, nullable=True),
        sa.Column('extraction_status', sa.String(20), server_default='pending'),
        sa.Column('extraction_id', UUID(as_uuid=True), nullable=True),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('source_metadata', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_documents_candidate_id', 'documents', 'candidate_profiles', ['candidate_id'], ['id'])
    op.create_index('idx_documents_candidate_id', 'documents', ['candidate_id'])
    
    # 8. Create extraction_results table
    op.create_table(
        'extraction_results',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('candidate_id', UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', UUID(as_uuid=True), nullable=True),
        sa.Column('extraction_type', sa.String(50), nullable=False),
        sa.Column('extraction_version', sa.String(20), nullable=True),
        sa.Column('extracted_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('extracted_data', sa.JSON, nullable=False),
        sa.Column('confidence_scores', sa.JSON, nullable=True),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('is_reconciled', sa.Boolean, server_default='false'),
        sa.Column('reconciled_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_extraction_results_candidate_id', 'extraction_results', 'candidate_profiles', ['candidate_id'], ['id'])
    op.create_foreign_key('fk_extraction_results_document_id', 'extraction_results', 'documents', ['document_id'], ['id'])
    
    # 9. Create extraction_fields table
    op.create_table(
        'extraction_fields',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('extraction_id', UUID(as_uuid=True), nullable=False),
        sa.Column('field_key', sa.String(100), nullable=False),
        sa.Column('field_category', sa.String(50), nullable=True),
        sa.Column('value', sa.Text, nullable=True),
        sa.Column('value_type', sa.String(50), nullable=True),
        sa.Column('source_text', sa.Text, nullable=True),
        sa.Column('source_location', sa.String(100), nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('confidence_reason', sa.Text, nullable=True),
        sa.Column('extraction_status', sa.String(20), server_default='extracted'),
        sa.Column('is_reconciled', sa.Boolean, server_default='false'),
        sa.Column('reconciliation_status', sa.String(20), nullable=True),
        sa.Column('metadata', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_foreign_key('fk_extraction_fields_extraction_id', 'extraction_fields', 'extraction_results', ['extraction_id'], ['id'])
    op.create_index('idx_extraction_fields_field_key', 'extraction_fields', ['field_key'])


def downgrade() -> None:
    """Drop M02 tables."""
    op.drop_table('extraction_fields')
    op.drop_table('extraction_results')
    op.drop_table('documents')
    op.drop_table('candidate_educations')
    op.drop_table('candidate_certifications')
    op.drop_table('candidate_skills')
    op.drop_table('professional_experiences')
    op.drop_table('candidate_profiles')
    op.drop_table('external_identities')
