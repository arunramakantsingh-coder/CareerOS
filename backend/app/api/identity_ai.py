from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.intelligence.ai_cv_ingestion import AICVIngestionError, ingest_cv_with_ai
from app.models.candidate_profile import CandidateProfile
from app.models.document import Document
from app.models.user import User

router = APIRouter(prefix="/identity", tags=["professional-profile-ai"])


@router.post("/documents/{document_id}/ai-reconcile")
def ai_reconcile_document(
    document_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Build the Professional Profile from a CV; other document types use Document Vault processing."""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == user.id,
        CandidateProfile.is_active.is_(True),
    ).first()
    if not profile:
        raise HTTPException(404, "Professional profile not found")

    document = db.query(Document).filter(
        Document.id == document_id,
        Document.candidate_id == profile.id,
    ).first()
    if not document:
        raise HTTPException(404, "Document not found")

    if (document.document_category or "").lower() != "cv":
        raise HTTPException(
            400,
            "This endpoint is only for CV profile building. Other documents belong to Document Vault processing.",
        )

    try:
        return ingest_cv_with_ai(document, profile, db)
    except AICVIngestionError as exc:
        raise HTTPException(422, str(exc)) from exc
