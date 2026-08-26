from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseResponse


class JobCreate(BaseModel):
    """Schema for creating/analyzing a job."""
    user_id: Optional[UUID] = None
    raw_jd: str = Field(..., min_length=50)
    source_name: Optional[str] = None
    source_url: Optional[str] = None


class JobUpdate(BaseModel):
    """Schema for updating a job."""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    remote_policy: Optional[str] = None
    is_active: Optional[bool] = None


class JobResponse(BaseResponse):
    """Schema for job response."""
    id: UUID
    user_id: Optional[UUID]
    title: Optional[str]
    company: Optional[str]
    location: Optional[str]
    remote_policy: Optional[str]
    salary_min: Optional[float]
    salary_max: Optional[float]
    salary_currency: Optional[str]
    is_processed: bool
    is_active: bool


class JobDNAResponse(BaseResponse):
    """Schema for Job DNA response."""
    id: UUID
    job_id: UUID
    role_family: Optional[str]
    seniority: Optional[str]
    capabilities: Optional[Dict[str, float]]
    skills: Optional[Dict[str, str]]
    mandatory_skills: Optional[Dict[str, str]]
    preferred_skills: Optional[Dict[str, str]]
    technologies: Optional[List[str]]
    experience_requirements: Optional[Dict[str, Any]]
    architecture_domains: Optional[List[str]]
    leadership_scope: Optional[Dict[str, Any]]
    governance_requirements: Optional[Dict[str, bool]]
    industry: Optional[str]
    location: Optional[Dict[str, Any]]
    mobility_requirements: Optional[Dict[str, Any]]
    education_requirements: Optional[Dict[str, str]]
    certifications_required: Optional[Dict[str, str]]
    summary: Optional[str]
    keywords: Optional[List[str]]
    confidence_score: Optional[float]
    completeness_score: Optional[float]
