from datetime import datetime
import uuid
from sqlalchemy import Column, DateTime, String, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin

class Application(Base, TimestampMixin):
    __tablename__ = "applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True)
    persona_id = Column(UUID(as_uuid=True), ForeignKey("personas.id"), nullable=True)
    advertised_title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    status = Column(String(40), nullable=False, default="DISCOVERED")
    package = Column(JSON, nullable=True)
    approved = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    applied_at = Column(DateTime, nullable=True)

class CompanyIntelligence(Base, TimestampMixin):
    __tablename__ = "company_intelligence"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    role_context = Column(Text, nullable=True)
    overview = Column(Text, nullable=True)
    technology_signals = Column(JSON, nullable=True)
    leadership_signals = Column(JSON, nullable=True)
    culture_signals = Column(JSON, nullable=True)
    sources = Column(JSON, nullable=True)

class Interview(Base, TimestampMixin):
    __tablename__ = "interviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    round_type = Column(String(80), nullable=False, default="General")
    scheduled_at = Column(DateTime, nullable=True)
    questions = Column(JSON, nullable=True)
    preparation = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    outcome = Column(String(40), nullable=True)

class TruthCheck(Base, TimestampMixin):
    __tablename__ = "truth_checks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    status = Column(String(30), nullable=False)
    claims = Column(JSON, nullable=True)
    issues = Column(JSON, nullable=True)

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(80), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    details = Column(JSON, nullable=True)

class LiveInterviewSession(Base, TimestampMixin):
    __tablename__ = "live_interview_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    active = Column(Boolean, default=True)
    transcript = Column(JSON, nullable=True)
    guidance = Column(JSON, nullable=True)
