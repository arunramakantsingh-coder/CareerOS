from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

from app.schemas.base import BaseResponse


class PersonaSkillWeightBase(BaseModel):
    """Base persona skill weight schema."""
    skill_id: UUID
    weight: float = Field(1.0, ge=0.0, le=2.0)
    importance: int = Field(1, ge=1, le=5)
    notes: Optional[str] = None


class PersonaSkillWeightCreate(PersonaSkillWeightBase):
    """Schema for creating a persona skill weight."""
    persona_id: UUID


class PersonaSkillWeightUpdate(BaseModel):
    """Schema for updating a persona skill weight."""
    weight: Optional[float] = Field(None, ge=0.0, le=2.0)
    importance: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class PersonaSkillWeightResponse(PersonaSkillWeightBase, BaseResponse):
    """Schema for persona skill weight response."""
    id: UUID
    persona_id: UUID
