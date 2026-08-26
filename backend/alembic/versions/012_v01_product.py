"""v0.1 product workflow tables"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid
revision = "012_v01_product"
down_revision = "011_authentication_foundation"
branch_labels = None
depends_on = None

def _table(name, columns):
    op.create_table(name, *columns)

def upgrade():
    common = lambda: [
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    ]
    _table("applications", common()+[
        sa.Column("job_id", UUID(as_uuid=True), sa.ForeignKey("jobs.id"), nullable=True),
        sa.Column("persona_id", UUID(as_uuid=True), sa.ForeignKey("personas.id"), nullable=True),
        sa.Column("advertised_title", sa.String(255), nullable=False), sa.Column("company", sa.String(255)),
        sa.Column("status", sa.String(40), nullable=False, server_default="DISCOVERED"), sa.Column("package", sa.JSON),
        sa.Column("approved", sa.Boolean, server_default="false"), sa.Column("notes", sa.Text), sa.Column("applied_at", sa.DateTime)])
    _table("company_intelligence", common()+[
        sa.Column("company_name", sa.String(255), nullable=False), sa.Column("role_context", sa.Text), sa.Column("overview", sa.Text),
        sa.Column("technology_signals", sa.JSON), sa.Column("leadership_signals", sa.JSON), sa.Column("culture_signals", sa.JSON), sa.Column("sources", sa.JSON)])
    _table("interviews", common()+[
        sa.Column("application_id", UUID(as_uuid=True), sa.ForeignKey("applications.id"), nullable=False), sa.Column("round_type", sa.String(80), server_default="General"),
        sa.Column("scheduled_at", sa.DateTime), sa.Column("questions", sa.JSON), sa.Column("preparation", sa.JSON), sa.Column("notes", sa.Text), sa.Column("outcome", sa.String(40))])
    _table("truth_checks", common()+[
        sa.Column("application_id", UUID(as_uuid=True), sa.ForeignKey("applications.id"), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("claims", sa.JSON), sa.Column("issues", sa.JSON)])
    _table("audit_logs", common()+[
        sa.Column("action", sa.String(100), nullable=False), sa.Column("entity_type", sa.String(80), nullable=False), sa.Column("entity_id", UUID(as_uuid=True)), sa.Column("details", sa.JSON)])
    _table("live_interview_sessions", common()+[
        sa.Column("application_id", UUID(as_uuid=True), sa.ForeignKey("applications.id"), nullable=False), sa.Column("active", sa.Boolean, server_default="true"), sa.Column("transcript", sa.JSON), sa.Column("guidance", sa.JSON)])

def downgrade():
    for name in ["live_interview_sessions","audit_logs","truth_checks","interviews","company_intelligence","applications"]:
        op.drop_table(name)
