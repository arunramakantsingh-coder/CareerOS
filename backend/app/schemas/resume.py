from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseResponse


class ResumeGenerateRequest(BaseModel):
    """Request to generate a resume."""
    user_id: UUID
    job_id: UUID
    persona_id: UUID


class ResumeSectionResponse(BaseResponse):
    """Response for a resume section."""
    id: UUID
    resume_id: UUID
    section_type: str
    section_title: Optional[str]
    order: int
    content: str
    source_evidence: Optional[List[Dict]]


class ResumeResponse(BaseResponse):
    """Response for a resume."""
    id: UUID
    user_id: UUID
    job_id: UUID
    persona_id: UUID
    version_number: int
    content: str
    format_type: str
    ats_score: Optional[float]
    keyword_coverage: Optional[float]
    truth_score: Optional[float]
    status: str


class ResumePreviewResponse(BaseModel):
    """Response for a resume preview."""
    content: str
    format_type: str
    ats_score: Optional[float]
    truth_score: Optional[float]
