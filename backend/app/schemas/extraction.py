from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class ExtractionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class ExtractionFieldStatus(str, Enum):
    EXTRACTED = "extracted"
    INFERRED = "inferred"
    USER_CONFIRMED = "user_confirmed"
    CONFLICTING = "conflicting"
    MISSING = "missing"


# ============================================
# EXTRACTION REQUEST
# ============================================

class ExtractionRequest(BaseModel):
    """Request to extract profile from a document."""
    document_id: UUID
    extraction_type: str = "cv"


# ============================================
# EXTRACTION FIELD
# ============================================

class ExtractionFieldResponse(BaseModel):
    """Extraction field response."""
    id: UUID
    extraction_id: UUID
    field_key: str
    field_category: Optional[str]
    value: Optional[str]
    value_type: Optional[str]
    source_text: Optional[str]
    confidence: Optional[float]
    extraction_status: str
    is_reconciled: bool
    created_at: datetime


# ============================================
# EXTRACTION RESULT
# ============================================

class ExtractionResultResponse(BaseModel):
    """Extraction result response."""
    id: UUID
    candidate_id: UUID
    document_id: Optional[UUID]
    extraction_type: str
    extraction_version: Optional[str]
    extracted_at: datetime
    status: str
    error_message: Optional[str]
    is_reconciled: bool
    reconciled_at: Optional[datetime]
    created_at: datetime


class ExtractionDetailResponse(ExtractionResultResponse):
    """Extraction result with fields."""
    fields: List[ExtractionFieldResponse]


# ============================================
# EXTRACTION SUMMARY
# ============================================

class ExtractionSummaryResponse(BaseModel):
    """Extraction summary."""
    total_documents: int
    processed_documents: int
    pending_documents: int
    failed_documents: int
    extraction_count: int
    last_extraction: Optional[datetime]


# ============================================
# PROFILE EXTRACTION RESULT
# ============================================

class ProfileExtractionResult(BaseModel):
    """Result of profile extraction."""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    linkedin_url: Optional[str] = None
    skills: List[Dict[str, Any]] = []
    experiences: List[Dict[str, Any]] = []
    certifications: List[Dict[str, Any]] = []
    educations: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    achievements: List[Dict[str, Any]] = []


class ExtractionConfidence(BaseModel):
    """Confidence scores for extraction."""
    overall: float
    personal: float
    professional: float
    technical: float
    credentials: float
