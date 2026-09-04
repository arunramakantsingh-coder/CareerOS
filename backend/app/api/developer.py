from __future__ import annotations

import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.roles import require_developer
from app.models.audit_log import AuditLog
from app.models.candidate_profile import CandidateProfile
from app.models.career_fact_evidence import CareerFactEvidence
from app.models.document import Document
from app.models.email_connector_account import EmailConnectorAccount
from app.models.persona import Persona
from app.models.persona_suggestion import PersonaSuggestion
from app.models.user import User

router = APIRouter(prefix="/developer", tags=["developer"])
STORAGE_ROOT = Path(__import__("os").getenv("CAREEROS_STORAGE_ROOT", "/app/storage/documents")).resolve()


@router.get("/status")
def developer_status(user: User = Depends(require_developer)):
    return {"developer_mode": True, "role": user.role, "email": user.email, "tools": ["reset_profile", "reset_parsed_data", "clear_test_documents", "clear_personas", "reset_email_connectors", "rerun_processing", "diagnostics"]}


@router.post("/reset-profile")
def reset_profile(user: User = Depends(require_developer), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        return {"reset": True, "message": "No profile data was present; login account was preserved."}
    documents = db.query(Document).filter(Document.candidate_id == profile.id).all()
    document_ids = [x.id for x in documents]
    db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id == profile.id).delete(synchronize_session=False)
    db.query(PersonaSuggestion).filter(PersonaSuggestion.user_id == user.id).delete(synchronize_session=False)
    db.query(Persona).filter(Persona.user_id == user.id).delete(synchronize_session=False)
    db.query(EmailConnectorAccount).filter(EmailConnectorAccount.user_id == user.id).delete(synchronize_session=False)
    for doc in documents:
        path = Path(doc.storage_path).resolve()
        if STORAGE_ROOT in path.parents and path.is_file():
            try: path.unlink()
            except OSError: pass
        db.delete(doc)
    # Clear candidate facts while keeping the candidate identity row and login account.
    for collection in (profile.experiences, profile.educations, profile.certifications, profile.skills):
        for item in list(collection): db.delete(item)
    profile.full_name = user.name; profile.location = None; profile.title = None; profile.summary = None; profile.linkedin_url = None; profile.primary_email = user.email; profile.primary_phone = None; profile.work_preferences = None; profile.years_experience = None; profile.industries = None; profile.seniority = None; profile.completeness_score = 0; profile.completeness_breakdown = None; profile.reconciliation_status = "pending"
    db.add(AuditLog(user_id=user.id, tenant_id=user.tenant_id, action="DEVELOPER_RESET_PROFILE", entity_type="candidate_profile", entity_id=profile.id, details={"documents_removed": len(document_ids), "login_preserved": True}))
    db.commit()
    return {"reset": True, "documents_removed": len(document_ids), "personas_removed": "all", "email_connectors_reset": True, "login_preserved": True}
