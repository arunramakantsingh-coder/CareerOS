from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class MigrationProfile(Base, TimestampMixin):
    """User's migration profile for eligibility checking."""
    
    __tablename__ = "migration_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Personal details
    age = Column(Integer, nullable=True)
    nationality = Column(String(100), nullable=True)
    country_of_residence = Column(String(100), nullable=True)
    
    # Qualifications
    education_level = Column(String(50), nullable=True)  # PhD, Masters, Bachelors, etc.
    field_of_study = Column(String(255), nullable=True)
    years_experience = Column(Integer, nullable=True)
    
    # Language
    english_level = Column(String(20), nullable=True)  # Proficient, Competent, Basic
    english_test = Column(String(50), nullable=True)  # IELTS, PTE, TOEFL
    english_score = Column(JSON, nullable=True)  # {"listening": 7, "reading": 7, ...}
    
    # Occupation
    occupation_title = Column(String(255), nullable=True)
    occupation_code = Column(String(20), nullable=True)  # ANZSCO or local code
    
    # Preferences
    target_countries = Column(JSON, nullable=True)
    target_visas = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="migration_profiles")
