from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class DiscoveryRequest(BaseModel):
    """Request to discover jobs."""
    user_id: UUID
    persona_id: UUID
    job_ids: Optional[List[UUID]] = None
    limit: Optional[int] = 50


class DiscoveryResult(BaseModel):
    """Individual discovery result."""
    job_id: str
    job_title: str
    company: Optional[str]
    location: Optional[str]
    overall_score: float
    title_match: Optional[float]
    capability_match: Optional[float]
    skill_match: Optional[float]
    responsibility_match: Optional[float]
    career_match: Optional[float]
    capability_details: Optional[Dict[str, Any]]
    skill_details: Optional[Dict[str, Any]]
    responsibility_details: Optional[Dict[str, Any]]
    career_details: Optional[Dict[str, Any]]
    discovery_rank: Optional[int]
    discovery_confidence: Optional[float]
    matched_capabilities: Optional[List[str]]
    missing_capabilities: Optional[List[str]]


class DiscoveryResponse(BaseModel):
    """Response for job discovery."""
    user_id: UUID
    persona_id: UUID
    total_discovered: int
    results: List[DiscoveryResult]
