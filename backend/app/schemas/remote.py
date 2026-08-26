from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseResponse


class RemoteEvaluationRequest(BaseModel):
    """Request to evaluate remote eligibility."""
    user_id: UUID
    job_id: UUID


class RemoteClassification(BaseModel):
    """Remote classification response."""
    job_id: UUID
    classification: str
    job_title: Optional[str]
    company: Optional[str]


class RemoteEvaluationResponse(BaseResponse):
    """Response for remote evaluation."""
    id: UUID
    user_id: UUID
    job_id: UUID
    remote_classification: Optional[str]
    overall_remote_score: float
    timezone_score: Optional[float]
    authorization_score: Optional[float]
    sponsorship_score: Optional[float]
    contractor_score: Optional[float]
    relocation_score: Optional[float]
    is_remote_eligible: bool
    is_timezone_compatible: bool
    has_work_authorization: bool
    requires_sponsorship: bool
    requires_relocation: bool
    allows_contractor: bool
    allows_eor: bool
    restrictions: Optional[List[str]]
    requirements: Optional[List[str]]
    remote_analysis: Optional[str]
