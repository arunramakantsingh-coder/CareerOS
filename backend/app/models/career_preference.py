from sqlalchemy import Column, String, Text, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class CareerPreference(Base, TimestampMixin):
    """Career preferences for a user."""
    
    __tablename__ = "career_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Work preferences
    work_mode = Column(String(20), nullable=True)  # On-site, Hybrid, Remote, Any
    preferred_locations = Column(JSON, nullable=True)  # List of preferred locations
    preferred_countries = Column(JSON, nullable=True)  # List of countries
    
    # Career preferences
    target_industries = Column(JSON, nullable=True)  # List of target industries
    target_role_families = Column(JSON, nullable=True)  # List of role families
    salary_expectations = Column(JSON, nullable=True)  # Min, max, currency
    
    # Mobility
    open_to_relocation = Column(String(10), default="false")  # true/false
    open_to_international = Column(String(10), default="false")  # true/false
    willing_to_travel = Column(String(10), default="false")  # true/false
    travel_percentage = Column(Integer, nullable=True)  # 0-100
    
    # Other
    visa_status = Column(String(50), nullable=True)
    work_authorization = Column(JSON, nullable=True)  # List of countries with authorization
    
    # Relationships
    user = relationship("User", back_populates="career_preferences")
