from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseResponse


class PersonaBase(BaseModel):
    """Base persona schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    target_titles: Optional[List[str]] = None
    target_industries: Optional[List[str]] = None
    target_locations: Optional[List[str]] = None
    target_companies: Optional[List[str]] = None
    preferred_seniority: Optional[str] = None
    salary_preferences: Optional[Dict[str, Any]] = None
    remote_preference: Optional[str] = None
    migration_preference: Optional[str] = None
    skill_weights: Optional[Dict[str, float]] = None
    capability_weights: Optional[Dict[str, float]] = None
    keywords: Optional[List[str]] = None
    positioning: Optional[str] = None
    is_active: bool = False
    is_default: bool = False


class PersonaCreate(PersonaBase):
    """Schema for creating a persona."""
    career_profile_id: UUID


class PersonaUpdate(PersonaBase):
    """Schema for updating a persona."""
    pass


class PersonaResponse(PersonaBase, BaseResponse):
    """Schema for persona response."""
    id: UUID
    user_id: UUID
    career_profile_id: UUID
    created_at: datetime
    updated_at: datetime
