from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS
# ============================================

class ExtractionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class DocumentCategory(str, Enum):
    CV = "cv"
    EMPLOYMENT = "employment"
    CERTIFICATION = "certification"
    EDUCATION = "education"
    PROJECT = "project"
    ACHIEVEMENT = "achievement"
    OTHER = "other"


# ============================================
# CANDIDATE PROFILE
# ============================================

class CandidateProfileBase(BaseModel):
    """Base candidate profile."""
    full_name: Optional[str] = None
    location: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    linkedin_url: Optional[str] = None
    linkedin_username: Optional[str] = None
    primary_email: Optional[str] = None
    primary_phone: Optional[str] = None
    work_preferences: Optional[Dict[str, Any]] = None
    years_experience: Optional[float] = None
    industries: Optional[List[str]] = None
    seniority: Optional[str] = None


class CandidateProfileCreate(CandidateProfileBase):
    """Create candidate profile."""
    user_id: UUID


class CandidateProfileUpdate(CandidateProfileBase):
    """Update candidate profile."""
    pass


class CandidateProfileResponse(CandidateProfileBase):
    """Candidate profile response."""
    id: UUID
    user_id: UUID
    completeness_score: Optional[float]
    completeness_breakdown: Optional[Dict[str, Any]]
    reconciliation_status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============================================
# PROFESSIONAL EXPERIENCE
# ============================================

class ProfessionalExperienceBase(BaseModel):
    """Base professional experience."""
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: bool = False
    responsibilities: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None


class ProfessionalExperienceCreate(ProfessionalExperienceBase):
    """Create professional experience."""
    candidate_id: UUID


class ProfessionalExperienceUpdate(ProfessionalExperienceBase):
    """Update professional experience."""
    pass


class ProfessionalExperienceResponse(ProfessionalExperienceBase):
    """Professional experience response."""
    id: UUID
    candidate_id: UUID
    is_reconciled: bool
    reconciliation_status: Optional[str]
    created_at: datetime
    updated_at: datetime


# ============================================
# SKILLS
# ============================================

class CandidateSkillBase(BaseModel):
    """Base candidate skill."""
    name: str
    category: Optional[str] = None
    proficiency: Optional[str] = None
    years_experience: Optional[float] = None
    last_used: Optional[str] = None


class CandidateSkillCreate(CandidateSkillBase):
    """Create candidate skill."""
    candidate_id: UUID


class CandidateSkillUpdate(CandidateSkillBase):
    """Update candidate skill."""
    pass


class CandidateSkillResponse(CandidateSkillBase):
    """Candidate skill response."""
    id: UUID
    candidate_id: UUID
    confidence: Optional[float]
    created_at: datetime
    updated_at: datetime


# ============================================
# CERTIFICATIONS
# ============================================

class CandidateCertificationBase(BaseModel):
    """Base candidate certification."""
    name: str
    issuer: str
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    credential_reference: Optional[str] = None
    credential_url: Optional[str] = None


class CandidateCertificationCreate(CandidateCertificationBase):
    """Create candidate certification."""
    candidate_id: UUID


class CandidateCertificationUpdate(CandidateCertificationBase):
    """Update candidate certification."""
    pass


class CandidateCertificationResponse(CandidateCertificationBase):
    """Candidate certification response."""
    id: UUID
    candidate_id: UUID
    confidence: Optional[float]
    created_at: datetime
    updated_at: datetime


# ============================================
# EDUCATION
# ============================================

class CandidateEducationBase(BaseModel):
    """Base candidate education."""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: bool = False
    grade: Optional[str] = None


class CandidateEducationCreate(CandidateEducationBase):
    """Create candidate education."""
    candidate_id: UUID


class CandidateEducationUpdate(CandidateEducationBase):
    """Update candidate education."""
    pass


class CandidateEducationResponse(CandidateEducationBase):
    """Candidate education response."""
    id: UUID
    candidate_id: UUID
    confidence: Optional[float]
    created_at: datetime
    updated_at: datetime


# ============================================
# DOCUMENTS
# ============================================

class DocumentBase(BaseModel):
    """Base document."""
    filename: str
    original_filename: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    document_category: Optional[str] = None
    document_subcategory: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Create document."""
    candidate_id: UUID
    storage_path: str


class DocumentResponse(DocumentBase):
    """Document response."""
    id: UUID
    candidate_id: UUID
    storage_url: Optional[str]
    status: str
    extraction_status: str
    created_at: datetime
    updated_at: datetime


class DocumentUploadRequest(BaseModel):
    """Document upload request."""
    filename: str
    content: str  # base64 encoded
    document_category: Optional[str] = None
    document_subcategory: Optional[str] = None


# ============================================
# PROFILE COMPLETENESS
# ============================================

class ProfileCompletenessResponse(BaseModel):
    """Profile completeness response."""
    overall_score: float
    breakdown: Dict[str, Any]  # {"Personal Information": 100, "Professional Experience": 80, ...}
    missing_items: List[str]
    suggestions: List[str]
