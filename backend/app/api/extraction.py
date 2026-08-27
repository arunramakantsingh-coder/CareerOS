from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.document import Document
from app.models.extraction_result import ExtractionResult
from app.models.extraction_field import ExtractionField
from app.schemas.extraction import (
    ExtractionRequest, ExtractionResultResponse, ExtractionDetailResponse,
    ExtractionFieldResponse, ExtractionSummaryResponse, ProfileExtractionResult
)
from app.utils.extraction_service import ExtractionService

router = APIRouter(prefix="/extraction", tags=["extraction"])
extraction_service = ExtractionService()


# ============================================
# EXTRACTION
# ============================================

@router.post("/extract", response_model=ExtractionResultResponse)
def extract_document(
    request: ExtractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract profile data from a document."""
    
    # Get document
    document = db.query(Document).filter(
        Document.id == request.document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Verify ownership
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.id == document.candidate_id,
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Run extraction
    result = extraction_service.extract_from_document(document, db)
    
    return result


@router.post("/extract-all")
def extract_all_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract all pending documents for the current user."""
    
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get pending documents
    documents = db.query(Document).filter(
        Document.candidate_id == profile.id,
        Document.extraction_status == "pending"
    ).all()
    
    results = []
    for doc in documents:
        result = extraction_service.extract_from_document(doc, db)
        results.append({"document_id": doc.id, "status": "processed"})
    
    return {"processed": len(results), "results": results}


# ============================================
# EXTRACTION RESULTS
# ============================================

@router.get("/results", response_model=List[ExtractionResultResponse])
def get_extraction_results(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all extraction results for the current user."""
    
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        return []
    
    results = db.query(ExtractionResult).filter(
        ExtractionResult.candidate_id == profile.id
    ).order_by(ExtractionResult.created_at.desc()).all()
    
    return results


@router.get("/results/{result_id}", response_model=ExtractionDetailResponse)
def get_extraction_detail(
    result_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed extraction result with fields."""
    
    result = db.query(ExtractionResult).filter(
        ExtractionResult.id == result_id
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extraction result not found"
        )
    
    # Verify ownership
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.id == result.candidate_id,
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Get fields
    fields = db.query(ExtractionField).filter(
        ExtractionField.extraction_id == result.id
    ).all()
    
    return {
        **result.__dict__,
        "fields": fields
    }


@router.get("/summary", response_model=ExtractionSummaryResponse)
def get_extraction_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get extraction summary for the current user."""
    
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        return ExtractionSummaryResponse(
            total_documents=0,
            processed_documents=0,
            pending_documents=0,
            failed_documents=0,
            extraction_count=0,
            last_extraction=None
        )
    
    # Count documents by status
    total_docs = db.query(Document).filter(
        Document.candidate_id == profile.id
    ).count()
    
    processed_docs = db.query(Document).filter(
        Document.candidate_id == profile.id,
        Document.extraction_status == "complete"
    ).count()
    
    pending_docs = db.query(Document).filter(
        Document.candidate_id == profile.id,
        Document.extraction_status == "pending"
    ).count()
    
    failed_docs = db.query(Document).filter(
        Document.candidate_id == profile.id,
        Document.extraction_status == "failed"
    ).count()
    
    # Get latest extraction
    last_extraction = db.query(ExtractionResult).filter(
        ExtractionResult.candidate_id == profile.id
    ).order_by(ExtractionResult.created_at.desc()).first()
    
    extraction_count = db.query(ExtractionResult).filter(
        ExtractionResult.candidate_id == profile.id
    ).count()
    
    return ExtractionSummaryResponse(
        total_documents=total_docs,
        processed_documents=processed_docs,
        pending_documents=pending_docs,
        failed_documents=failed_docs,
        extraction_count=extraction_count,
        last_extraction=last_extraction.created_at if last_extraction else None
    )


# ============================================
# PROFILE EXTRACTION
# ============================================

@router.get("/profile", response_model=ProfileExtractionResult)
def get_extracted_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's extracted profile data."""
    
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get latest extraction
    extraction = db.query(ExtractionResult).filter(
        ExtractionResult.candidate_id == profile.id,
        ExtractionResult.status == "complete"
    ).order_by(ExtractionResult.created_at.desc()).first()
    
    if not extraction:
        return ProfileExtractionResult()
    
    # Parse extracted data
    data = extraction.extracted_data or {}
    personal = data.get("personal", {})
    
    return ProfileExtractionResult(
        full_name=personal.get("name"),
        email=personal.get("email"),
        phone=personal.get("phone"),
        location=personal.get("location"),
        title=personal.get("title"),
        summary=personal.get("summary"),
        linkedin_url=personal.get("linkedin"),
        skills=data.get("skills", []),
        experiences=data.get("professional", []),
        certifications=data.get("certifications", []),
        educations=data.get("education", []),
        projects=data.get("projects", []),
        achievements=data.get("achievements", [])
    )
