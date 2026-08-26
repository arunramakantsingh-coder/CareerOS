from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class ResumeSection(Base, TimestampMixin):
    """Individual section of a resume."""
    
    __tablename__ = "resume_sections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resume_versions.id"), nullable=False)
    
    # Section info
    section_type = Column(String(50), nullable=False)  # summary, experience, skills, education, certifications, projects
    section_title = Column(String(100), nullable=True)
    order = Column(Integer, nullable=False, default=0)
    
    # Content
    content = Column(Text, nullable=False)
    source_evidence = Column(JSON, nullable=True)  # References to evidence used
    
    # Relationships
    resume = relationship("ResumeVersion", back_populates="sections")
    evidence_links = relationship("ResumeEvidenceLink", back_populates="section", cascade="all, delete-orphan")
