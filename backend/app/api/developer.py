from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.roles import require_developer
from app.models.candidate_profile import CandidateProfile
from app.models.career_fact_evidence import CareerFactEvidence
from app.models.document import Document
from app.models.email_connector_account import EmailConnectorAccount
from app.models.external_identity import ExternalIdentity
from app.models.persona import Persona
from app.models.persona_suggestion import PersonaSuggestion
from app.models.user import User
from app.models.v01_product import AuditLog

router = APIRouter(prefix="/developer", tags=["developer"])
STORAGE_ROOT = Path(os.getenv("CAREEROS_STORAGE_ROOT", "/app/storage/documents")).resolve()
RESET_SCOPES = {"career_data", "documents", "personas", "connections", "all"}


class ResetRequest(BaseModel):
    scope: Literal["career_data", "documents", "personas", "connections", "all"] = "career_data"


def _remove_document_files(documents: list[Document]) -> int:
    removed = 0
    for doc in documents:
        path = Path(doc.storage_path).resolve()
        if STORAGE_ROOT in path.parents and path.is_file():
            try:
                path.unlink()
                removed += 1
            except OSError:
                pass
    return removed


def _reset_connections(db: Session, user: User) -> dict[str, int]:
    # Preserve Google identity records used for sign-in, but remove mailbox tokens.
    gmail_tokens_cleared = 0
    identities = db.query(ExternalIdentity).filter(ExternalIdentity.user_id == user.id).all()
    for identity in identities:
        scopes = identity.scopes or []
        if identity.provider == "google" and "https://www.googleapis.com/auth/gmail.readonly" in scopes:
            identity.access_token = None
            identity.refresh_token = None
            identity.token_expires_at = None
            identity.scopes = []
            identity.last_used = None
            gmail_tokens_cleared += 1
    connector_count = db.query(EmailConnectorAccount).filter(EmailConnectorAccount.user_id == user.id).delete(synchronize_session=False)
    return {"gmail_tokens_cleared": gmail_tokens_cleared, "connector_accounts_removed": connector_count}


@router.get("/status")
def developer_status(user: User = Depends(require_developer)):
    return {
        "developer_mode": True,
        "role": user.role,
        "email": user.email,
        "tools": ["project_tracker", "bug_tracker", "version_history", "rollback_guidance", "reset_test_data", "diagnostics"],
        "reset_scopes": sorted(RESET_SCOPES),
    }


@router.get("/diagnostics")
def developer_diagnostics(user: User = Depends(require_developer), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    return {
        "developer_mode": True,
        "application": os.getenv("CAREEROS_APP_NAME", "CareerOS"),
        "version": os.getenv("CAREEROS_VERSION", "development"),
        "git_commit": os.getenv("CAREEROS_GIT_COMMIT", "unknown"),
        "git_branch": os.getenv("CAREEROS_GIT_BRANCH", "unknown"),
        "environment": os.getenv("CAREEROS_ENV", "development"),
        "profile_present": bool(profile),
        "profile_id": str(profile.id) if profile else None,
        "reset_scopes": sorted(RESET_SCOPES),
        "github_repository": "https://github.com/arunramakantsingh-coder/CareerOS",
    }


@router.post("/reset")
def reset_test_data(request: ResetRequest, user: User = Depends(require_developer), db: Session = Depends(get_db)):
    scope = request.scope
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    documents_removed = 0
    personas_removed = 0
    evidence_removed = 0
    connection_result = {"gmail_tokens_cleared": 0, "connector_accounts_removed": 0}

    if profile and scope in {"career_data", "documents", "personas", "all"}:
        documents = db.query(Document).filter(Document.candidate_id == profile.id).all()
        if scope in {"documents", "all"}:
            documents_removed = _remove_document_files(documents)
            for doc in documents:
                db.delete(doc)

        if scope in {"career_data", "all"}:
            evidence_removed = db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id == profile.id).delete(synchronize_session=False)
            for collection in (profile.experiences, profile.educations, profile.certifications, profile.skills):
                for item in list(collection):
                    db.delete(item)
            profile.full_name = user.name
            profile.location = None
            profile.title = None
            profile.summary = None
            profile.linkedin_url = None
            profile.primary_email = user.email
            profile.primary_phone = None
            profile.work_preferences = None
            profile.years_experience = None
            profile.industries = None
            profile.seniority = None
            profile.completeness_score = 0
            profile.completeness_breakdown = None
            profile.reconciliation_status = "pending"

        if scope in {"personas", "all"}:
            personas_removed += db.query(PersonaSuggestion).filter(PersonaSuggestion.user_id == user.id).delete(synchronize_session=False)
            personas_removed += db.query(Persona).filter(Persona.user_id == user.id).delete(synchronize_session=False)

    if scope in {"connections", "all"}:
        connection_result = _reset_connections(db, user)

    db.add(
        AuditLog(
            user_id=user.id,
            tenant_id=user.tenant_id,
            action="DEVELOPER_RESET_TEST_DATA",
            entity_type="developer_control",
            entity_id=user.id,
            details={
                "scope": scope,
                "documents_removed": documents_removed,
                "evidence_removed": evidence_removed,
                "personas_removed": personas_removed,
                **connection_result,
                "login_preserved": True,
            },
        )
    )
    db.commit()

    return {
        "reset": True,
        "scope": scope,
        "documents_removed": documents_removed,
        "evidence_removed": evidence_removed,
        "personas_removed": personas_removed,
        **connection_result,
        "login_preserved": True,
    }


@router.post("/reset-profile")
def reset_profile(user: User = Depends(require_developer), db: Session = Depends(get_db)):
    # Backward-compatible alias used by the existing Developer Mode UI.
    return reset_test_data(ResetRequest(scope="all"), user, db)
