from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.core.security import get_current_user
from app.intelligence.ai_cv_ingestion import AICVIngestionError, ingest_cv_with_ai
from app.intelligence.profile_validation import ProfileValidationError, validate_reconciled_profile
from app.models.candidate_profile import CandidateProfile
from app.models.document import Document
from app.models.user import User

router = APIRouter(prefix="/identity", tags=["professional-identity-jobs"])


def _profile(user: User, db: Session) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id, CandidateProfile.is_active.is_(True)).first()
    if not profile:
        raise HTTPException(404, "Professional profile not found")
    return profile


def _set_status(document: Document, job_id: str, stage: str, message: str, progress: int, status: str = "running", error: str | None = None) -> None:
    payload = dict(document.processing_status or {})
    payload.update({"job_id": job_id, "status": status, "stage": stage, "message": message, "progress": progress, "updated_at": datetime.now(timezone.utc).isoformat()})
    if error:
        payload["error"] = error
    elif "error" in payload:
        payload.pop("error", None)
    document.processing_status = payload
    document.processing_stage = stage
    document.status = "processing" if status == "running" else ("failed" if status == "failed" else document.status)


def _run_reconciliation(document_id: UUID, profile_id: UUID, job_id: str) -> None:
    db = SessionLocal()
    document = None
    try:
        document = db.query(Document).filter(Document.id == document_id, Document.candidate_id == profile_id).first()
        profile = db.query(CandidateProfile).filter(CandidateProfile.id == profile_id).first()
        if not document or not profile:
            return
        _set_status(document, job_id, "validating_document", "Validating CV and stored source text", 10)
        db.commit()
        if document.document_category != "cv":
            raise AICVIngestionError("AI profile building is only supported for CV documents")
        extracted = (document.source_metadata or {}).get("extracted_text", "")
        if not isinstance(extracted, str) or not extracted.strip():
            raise AICVIngestionError("No stored CV source text is available")
        _set_status(document, job_id, "routing", "Selecting the Global Intelligence Engine route", 20)
        db.commit()
        _set_status(document, job_id, "ai_processing", "Waiting for the selected AI provider to return the structured CV profile", 30)
        db.commit()
        result = ingest_cv_with_ai(document, profile, db)
        _set_status(document, job_id, "reconciling_profile", "Reconciling AI-extracted facts into the Professional Profile", 70)
        db.commit()
        _set_status(document, job_id, "profile_validation", "Running final AI validation against the populated Professional Profile", 85)
        db.commit()
        try:
            validation = validate_reconciled_profile(document, profile, db)
        except ProfileValidationError as exc:
            validation = {
                "status": "needs_review",
                "summary": "Post-reconciliation AI validation returned an invalid validation payload.",
                "issues": [{"section": "profile", "type": "validation_parse_error", "severity": "warning", "description": str(exc)[:500]}],
                "duplicate_candidates": [],
            }
        metadata = dict(document.source_metadata or {})
        metadata["ai_profile_validation"] = validation
        document.source_metadata = metadata
        _set_status(document, job_id, "persisting", "Persisting the validated Professional Profile result", 95)
        db.commit()
        _set_status(document, job_id, "completed", "CV reconciliation completed", 100, status="completed")
        payload = dict(document.processing_status or {})
        payload["result"] = {**result, "validation": validation}
        document.processing_status = payload
        db.commit()
    except Exception as exc:
        if document:
            # The AI pipeline is transactional: a failed run must not leave a half-built profile.
            failed_stage = (document.processing_status or {}).get("stage") or "unknown"
            db.rollback()
            document = db.query(Document).filter(Document.id == document_id, Document.candidate_id == profile_id).first()
            if document:
                payload = dict(document.processing_status or {})
                payload.update({"job_id": job_id, "status": "failed", "stage": "failed", "failed_stage": failed_stage, "message": "CV reconciliation failed", "progress": 100, "updated_at": datetime.now(timezone.utc).isoformat(), "error": str(exc)[:1000]})
                document.processing_status = payload
                document.processing_stage = "failed"
                document.status = "failed"
                db.commit()
    finally:
        db.close()


@router.post("/documents/{document_id}/ai-reconcile-job", status_code=202)
def start_ai_reconciliation_job(document_id: UUID, background_tasks: BackgroundTasks, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _profile(user, db)
    document = db.query(Document).filter(Document.id == document_id, Document.candidate_id == profile.id).first()
    if not document:
        raise HTTPException(404, "Document not found")
    if document.document_category != "cv":
        raise HTTPException(400, "AI profile building is only available for CV documents")
    existing = document.processing_status or {}
    if existing.get("status") == "running":
        return {"status": "accepted", "job_id": existing.get("job_id"), "document_id": str(document.id)}
    job_id = str(uuid4())
    _set_status(document, job_id, "queued", "CV reconciliation queued", 0)
    db.commit()
    background_tasks.add_task(_run_reconciliation, document.id, profile.id, job_id)
    return {"status": "accepted", "job_id": job_id, "document_id": str(document.id)}


@router.get("/documents/{document_id}/ai-reconcile-job/{job_id}")
def get_ai_reconciliation_job(document_id: UUID, job_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _profile(user, db)
    document = db.query(Document).filter(Document.id == document_id, Document.candidate_id == profile.id).first()
    if not document:
        raise HTTPException(404, "Document not found")
    status = document.processing_status or {}
    if status.get("job_id") != job_id:
        raise HTTPException(404, "Reconciliation job not found")
    return {"status": status.get("status", "unknown"), "job_id": job_id, "document_id": str(document.id), "stage": status.get("stage"), "failed_stage": status.get("failed_stage"), "message": status.get("message"), "progress": status.get("progress", 0), "updated_at": status.get("updated_at"), "error": status.get("error"), "result": status.get("result")}
