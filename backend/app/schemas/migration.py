from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseResponse


# ============================================
# Country Schemas
# ============================================

class CountryResponse(BaseResponse):
    """Country response schema."""
    id: UUID
    code: str
    name: str
    region: Optional[str]
    immigration_authority: Optional[str]
    official_website: Optional[str]
    is_active: bool
    description: Optional[str]
    meta_data: Optional[Dict[str, Any]]


# ============================================
# Visa Schemas
# ============================================

class VisaResponse(BaseResponse):
    """Visa response schema."""
    id: UUID
    country_id: UUID
    code: str
    name: str
    category: Optional[str]
    description: Optional[str]
    is_active: bool


# ============================================
# Migration Rule Schemas
# ============================================

class MigrationRuleResponse(BaseResponse):
    """Migration rule response schema."""
    id: UUID
    visa_id: UUID
    rule_key: str
    rule_type: str
    rule_value: Dict[str, Any]
    description: Optional[str]
    condition_text: Optional[str]
    effective_from: datetime
    effective_to: Optional[datetime]
    is_current: bool
    source_type: Optional[str]
    source_url: Optional[str]
    source_reference: Optional[str]
    verified_at: Optional[datetime]
    verified_by: Optional[str]


# ============================================
# Pathway Schemas
# ============================================

class PathwayResponse(BaseResponse):
    """Migration pathway response schema."""
    id: UUID
    visa_id: UUID
    name: str
    description: Optional[str]
    pathway_type: str
    requirements: Optional[Dict[str, Any]]
    points_required: Optional[int]
    is_active: bool
    is_current: bool


# ============================================
# Migration Profile Schemas
# ============================================

class MigrationProfileCreate(BaseModel):
    """Migration profile creation schema."""
    user_id: UUID
    age: Optional[int] = None
    nationality: Optional[str] = None
    country_of_residence: Optional[str] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    years_experience: Optional[int] = None
    english_level: Optional[str] = None
    english_test: Optional[str] = None
    english_score: Optional[Dict[str, Any]] = None
    occupation_title: Optional[str] = None
    occupation_code: Optional[str] = None
    target_countries: Optional[List[str]] = None
    target_visas: Optional[List[str]] = None


class MigrationProfileUpdate(BaseModel):
    """Migration profile update schema."""
    age: Optional[int] = None
    nationality: Optional[str] = None
    country_of_residence: Optional[str] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    years_experience: Optional[int] = None
    english_level: Optional[str] = None
    english_test: Optional[str] = None
    english_score: Optional[Dict[str, Any]] = None
    occupation_title: Optional[str] = None
    occupation_code: Optional[str] = None
    target_countries: Optional[List[str]] = None
    target_visas: Optional[List[str]] = None


class MigrationProfileResponse(BaseResponse):
    """Migration profile response schema."""
    id: UUID
    user_id: UUID
    age: Optional[int]
    nationality: Optional[str]
    country_of_residence: Optional[str]
    education_level: Optional[str]
    field_of_study: Optional[str]
    years_experience: Optional[int]
    english_level: Optional[str]
    english_test: Optional[str]
    english_score: Optional[Dict[str, Any]]
    occupation_title: Optional[str]
    occupation_code: Optional[str]
    target_countries: Optional[List[str]]
    target_visas: Optional[List[str]]


# ============================================
# Eligibility Schemas
# ============================================

class EligibilityRequest(BaseModel):
    """Eligibility check request."""
    user_id: UUID
    country_code: str
    visa_code: Optional[str] = None


class EligibilityResponse(BaseModel):
    """Eligibility check response."""
    country: str
    visa_code: Optional[str]
    overall_eligibility: float
    eligibility_status: str
    requirements_met: List[str]
    requirements_partial: List[str]
    requirements_not_met: List[str]
    pathways: List[str]
    score: float
    recommendations: List[str]
    disclaimer: str
    sources: List[Dict[str, Any]]

