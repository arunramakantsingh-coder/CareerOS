from sqlalchemy import Column, String, Text, JSON, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class JobDNA(Base, TimestampMixin):
    """Job DNA - structured semantic representation of a job."""
    
    __tablename__ = "job_dna"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    # Core identity
    role_family = Column(String(100), nullable=True)  # Network Architect, Security Engineer, etc.
    seniority = Column(String(50), nullable=True)  # Entry, Mid, Senior, Lead, Manager, Director, Executive
    
    # Capabilities and skills
    capabilities = Column(JSON, nullable=True)  # {"capability": "importance"}
    skills = Column(JSON, nullable=True)  # {"skill": "requirement_level"}
    mandatory_skills = Column(JSON, nullable=True)  # Skills marked as required
    preferred_skills = Column(JSON, nullable=True)  # Skills marked as preferred
    
    # Technologies
    technologies = Column(JSON, nullable=True)  # {"technology": "proficiency"}
    
    # Experience
    experience_requirements = Column(JSON, nullable=True)  # {"minimum": 3, "preferred": 5, "fields": [...]}
    
    # Architecture domains
    architecture_domains = Column(JSON, nullable=True)  # List of domains
    leadership_scope = Column(JSON, nullable=True)  # {"people": 0, "budget": 0, "strategic": False}
    governance_requirements = Column(JSON, nullable=True)  # {"risk": True, "compliance": True, "policy": True}
    
    # Industry and context
    industry = Column(String(100), nullable=True)
    industry_context = Column(Text, nullable=True)
    
    # Location and mobility
    location = Column(JSON, nullable=True)  # {"country": "US", "city": "New York", "remote": True}
    mobility_requirements = Column(JSON, nullable=True)  # {"relocation": True, "sponsorship": False, "visa_required": True}
    
    # Education and certifications
    education_requirements = Column(JSON, nullable=True)  # {"degree": "Bachelor's", "field": "Computer Science"}
    certifications_required = Column(JSON, nullable=True)  # {"certification": "importance"}
    
    # Additional metadata
    summary = Column(Text, nullable=True)  # AI-generated summary
    keywords = Column(JSON, nullable=True)  # Extracted keywords
    embedding = Column(JSON, nullable=True)  # For semantic search (pgvector compatible)
    
    # Quality metrics
    confidence_score = Column(Float, nullable=True)  # Overall confidence in extraction
    completeness_score = Column(Float, nullable=True)  # How complete the DNA is
    
    # Relationships
    job = relationship("Job", back_populates="job_dna")
