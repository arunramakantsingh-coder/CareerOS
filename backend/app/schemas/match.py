from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseResponse


class MatchRequest(BaseModel):
    """Request to run a match."""
    user_id: UUID
    job_id: UUID
    persona_id: UUID


class MatchDimensionResponse(BaseResponse):
    """Response for a match dimension."""
    id: UUID
    match_id: UUID
    name: str
    score: float
    weight: float
    matched_items: Optional[List[Any]]
    partial_items: Optional[List[Any]]
    missing_items: Optional[List[Any]]
    explanation: Optional[str]


class MatchRecommendationResponse(BaseResponse):
    """Response for a match recommendation."""
    id: UUID
    match_id: UUID
    category: str
    priority: Optional[str]
    recommendation: str
    action_required: Optional[str]
    impact: Optional[str]
    difficulty: Optional[str]


class MatchResponse(BaseResponse):
    """Response for a match."""
    id: UUID
    user_id: UUID
    job_id: UUID
    persona_id: UUID
    overall_score: float
    dimension_scores: Dict[str, float]
    status: Optional[str]
    summary: Optional[str]
    recommendation: Optional[str]
    matched_skills: Optional[List[Any]]
    partial_skills: Optional[List[Any]]
    missing_skills: Optional[List[Any]]
    hard_failures: Optional[List[Any]]
    gaps: Optional[Dict[str, List[str]]]
    risks: Optional[List[str]]
