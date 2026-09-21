from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class ExtractionStatus(str):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class DocumentCategory(str):
    CV = "cv"
    EMPLOYMENT = "employment"
    CERTIFICATION = "certification"
    EDUCATION = "education"
    PROJECT = "project"
    ACHIEVEMENT = "achievement"
    OTHER = "other"


class CandidateProfileBase(BaseModel):
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
    user_id: UUID


class CandidateProfileUpdate(CandidateProfileBase):
    pass


class CandidateProfileResponse(CandidateProfileBase):
    id: UUID
    user_id: UUID
    completeness_score: Optional[float] = None
    completeness_breakdown: Optional[Dict[str, Any]] = None
    reconciliation_status: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfessionalExperienceBase(BaseModel):
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
    candidate_id: UUID


class ProfessionalExperienceUpdate(ProfessionalExperienceBase):
    pass


class ProfessionalExperienceResponse(ProfessionalExperienceBase):
    id: UUID
    candidate_id: UUID
    is_reconciled: Optional[bool] = None
    reconciliation_status: Optional[str] = None
    confidence: Optional[float] = None
    source_type: Optional[str] = None
    source_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class CandidateSkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    proficiency: Optional[str] = None
    years_experience: Optional[float] = None
    last_used: Optional[str] = None


class CandidateSkillCreate(CandidateSkillBase):
    candidate_id: UUID


class CandidateSkillUpdate(CandidateSkillBase):
    pass


class CandidateSkillResponse(CandidateSkillBase):
    id: UUID
    candidate_id: UUID
    confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class CandidateCertificationBase(BaseModel):
    name: str
    issuer: str
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    credential_reference: Optional[str] = None
    credential_url: Optional[str] = None


class CandidateCertificationCreate(CandidateCertificationBase):
    candidate_id: UUID


class CandidateCertificationUpdate(CandidateCertificationBase):
    pass


class CandidateCertificationResponse(CandidateCertificationBase):
    id: UUID
    candidate_id: UUID
    confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class CandidateEducationBase(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: bool = False
    grade: Optional[str] = None


class CandidateEducationCreate(CandidateEducationBase):
    candidate_id: UUID


class CandidateEducationUpdate(CandidateEducationBase):
    pass


class CandidateEducationResponse(CandidateEducationBase):
    id: UUID
    candidate_id: UUID
    confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class DocumentBase(BaseModel):
    filename: str
    original_filename: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    document_category: Optional[str] = None
    document_subcategory: Optional[str] = None


class DocumentCreate(DocumentBase):
    candidate_id: UUID
    storage_path: str


class DocumentResponse(DocumentBase):
    id: UUID
    candidate_id: UUID
    storage_url: Optional[str] = None
    status: str
    extraction_status: str
    user_label: Optional[str] = None
    detected_type: Optional[str] = None
    classification_confidence: Optional[float] = None
    classification_reason: Optional[str] = None
    verification_status: Optional[str] = None
    processing_stage: Optional[str] = None
    content_hash: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    document_number: Optional[str] = None
    batch_id: Optional[UUID] = None
    is_zip_content: bool = False
    parent_zip_id: Optional[UUID] = None
    source: Optional[str] = None
    source_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class DocumentUploadRequest(BaseModel):
    filename: str
    content: str
    document_category: Optional[str] = None
    document_subcategory: Optional[str] = None


class ProfileCompletenessResponse(BaseModel):
    overall_score: float
    breakdown: Dict[str, Any]
    missing_items: List[str]
    suggestions: List[str]
