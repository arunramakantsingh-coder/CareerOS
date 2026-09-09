from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.intelligence.identity_reconciliation import IdentityReconciliationError, reconcile_document_employment
from app.models.candidate_profile import CandidateProfile
from app.models.document import Document
from app.models.user import User

router = APIRouter(prefix="/identity", tags=["professional-identity-ai"])


@router.post("/documents/{document_id}/ai-reconcile")
def ai_reconcile_document(document_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Run controlled AI reconciliation for one owner-scoped CV/employment document."""
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
    if document.document_category not in {"cv", "employment", "other"}:
        raise HTTPException(400, "AI employment reconciliation is only available for CV or employment documents")

    try:
        return reconcile_document_employment(document, db)
    except IdentityReconciliationError as exc:
        raise HTTPException(422, str(exc)) from exc
