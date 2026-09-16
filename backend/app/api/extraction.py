from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.intelligence.ai_cv_ingestion import AICVIngestionError, ingest_cv_with_ai
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.document import Document
from app.models.extraction_result import ExtractionResult
from app.models.extraction_field import ExtractionField
from app.schemas.extraction import (
    ExtractionResultResponse, ExtractionDetailResponse,
    ExtractionFieldResponse, ExtractionSummaryResponse, ProfileExtractionResult
)

router = APIRouter(prefix="/extraction", tags=["extraction"])


@router.post("/extract")
def extract_document(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Legacy extraction endpoint retained as a compatibility route; CV extraction is AI-only."""
    document_id = request.get("document_id") if isinstance(request, dict) else None
    if not document_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="document_id is required")

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == document.candidate_id, CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if document.document_category != "cv":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AI extraction is currently supported for CV documents only")

    try:
        return ingest_cv_with_ai(document, profile, db)
    except AICVIngestionError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/extract-all")
def extract_all_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Compatibility endpoint that explicitly reconciles pending CV documents with AI."""
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id, CandidateProfile.is_active.is_(True)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    documents = db.query(Document).filter(Document.candidate_id == profile.id, Document.document_category == "cv").all()
    results = []
    for document in documents:
        try:
            results.append(ingest_cv_with_ai(document, profile, db))
        except AICVIngestionError as exc:
            db.rollback()
            results.append({"document_id": str(document.id), "status": "failed", "error": str(exc)})
    return {"processed": sum(1 for x in results if x.get("status") in {"complete", "conflicting"}), "results": results}


@router.get("/results", response_model=List[ExtractionResultResponse])
def get_extraction_results(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id, CandidateProfile.is_active.is_(True)).first()
    if not profile:
        return []
    return db.query(ExtractionResult).filter(ExtractionResult.candidate_id == profile.id).order_by(ExtractionResult.created_at.desc()).all()


@router.get("/results/{result_id}", response_model=ExtractionDetailResponse)
def get_extraction_detail(result_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = db.query(ExtractionResult).filter(ExtractionResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extraction result not found")
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == result.candidate_id, CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    fields = db.query(ExtractionField).filter(ExtractionField.extraction_id == result.id).all()
    return {**result.__dict__, "fields": fields}


@router.get("/summary", response_model=ExtractionSummaryResponse)
def get_extraction_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id, CandidateProfile.is_active.is_(True)).first()
    if not profile:
        return ExtractionSummaryResponse(total_documents=0, processed_documents=0, pending_documents=0, failed_documents=0, extraction_count=0, last_extraction=None)
    total_docs = db.query(Document).filter(Document.candidate_id == profile.id).count()
    processed_docs = db.query(Document).filter(Document.candidate_id == profile.id, Document.extraction_status == "complete").count()
    pending_docs = db.query(Document).filter(Document.candidate_id == profile.id, Document.extraction_status == "pending").count()
    failed_docs = db.query(Document).filter(Document.candidate_id == profile.id, Document.extraction_status == "failed").count()
    last_extraction = db.query(ExtractionResult).filter(ExtractionResult.candidate_id == profile.id).order_by(ExtractionResult.created_at.desc()).first()
    extraction_count = db.query(ExtractionResult).filter(ExtractionResult.candidate_id == profile.id).count()
    return ExtractionSummaryResponse(total_documents=total_docs, processed_documents=processed_docs, pending_documents=pending_docs, failed_documents=failed_docs, extraction_count=extraction_count, last_extraction=last_extraction.created_at if last_extraction else None)


@router.get("/profile", response_model=ProfileExtractionResult)
def get_extracted_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id, CandidateProfile.is_active.is_(True)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    extraction = db.query(ExtractionResult).filter(ExtractionResult.candidate_id == profile.id, ExtractionResult.status == "complete").order_by(ExtractionResult.created_at.desc()).first()
    if not extraction:
        return ProfileExtractionResult()
    data = extraction.extracted_data or {}
    personal = data.get("profile", {})
    return ProfileExtractionResult(
        full_name=personal.get("full_name"),
        email=personal.get("email"),
        phone=personal.get("phone"),
        location=personal.get("location"),
        title=personal.get("title"),
        summary=personal.get("summary"),
        linkedin_url=personal.get("linkedin"),
        skills=data.get("skills", []),
        experiences=data.get("employment", []),
        certifications=data.get("certifications", []),
        educations=data.get("education", []),
        projects=data.get("projects", []),
        achievements=data.get("accomplishments", []),
    )
