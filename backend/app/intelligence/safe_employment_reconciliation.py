from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.intelligence.identity_reconciliation import _best_match, _date, _ensure_evidence, _find_verified_match
from app.models.document import Document
from app.models.professional_experience import ProfessionalExperience


MUTABLE_RECONCILIATION_STATUSES = ("extracted", "ai_reconciled", "ai_review")


def apply_experiences_source_scoped(
    document: Document,
    experiences: list[dict[str, Any]],
    db: Session,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Apply AI employment proposals without cross-document mutation or destructive pruning.

    User-confirmed Career Vault facts are always protected. Mutable records may only be
    updated when they belong to the same source document. Records from another document
    are left untouched, and missing matches are created as new document-sourced facts.
    """
    candidate_id = document.candidate_id
    applied: list[dict[str, Any]] = []
    needs_review: list[dict[str, Any]] = []
    protected: list[dict[str, Any]] = []

    for exp in experiences:
        confidence = float(exp.get("confidence") or 0.0)

        verified = _find_verified_match(exp, candidate_id, db)
        if verified is not None:
            _ensure_evidence(document, verified, confidence, exp.get("evidence_excerpt"), db)
            protected.append(
                {
                    "experience_id": str(verified.id),
                    "organization": verified.company,
                    "title": verified.title,
                    "confidence": confidence,
                }
            )
            continue

        target = _find_mutable_experience_source_scoped(exp, candidate_id, document.id, db)
        if target is None:
            target = ProfessionalExperience(candidate_id=candidate_id)
            db.add(target)

        target.company = exp["organization"]
        target.client = exp.get("client")
        target.title = exp["title"]
        target.start_date = _date(exp.get("start_date"))
        target.end_date = _date(exp.get("end_date"))
        target.is_current = bool(exp.get("is_current"))
        target.responsibilities = exp.get("responsibilities") or []
        target.achievements = exp.get("achievements") or []
        target.technologies = exp.get("technologies") or []
        target.industries = exp.get("industries") or []
        target.industry = target.industries[0] if target.industries else target.industry
        target.source_type = "document"
        target.source_id = document.id
        target.is_reconciled = confidence >= 0.85
        target.reconciliation_status = "ai_reconciled" if confidence >= 0.85 else "ai_review"
        db.flush()

        _ensure_evidence(document, target, confidence, exp.get("evidence_excerpt"), db)
        item = {
            "experience_id": str(target.id),
            "organization": target.company,
            "client": target.client,
            "title": target.title,
            "confidence": confidence,
        }
        (applied if confidence >= 0.85 else needs_review).append(item)

    return applied, needs_review, protected


def _find_mutable_experience_source_scoped(
    exp: dict[str, Any],
    candidate_id: UUID,
    document_id: UUID,
    db: Session,
) -> ProfessionalExperience | None:
    """Find only mutable employment belonging to the current source document."""
    rows = db.query(ProfessionalExperience).filter(
        ProfessionalExperience.candidate_id == candidate_id,
        ProfessionalExperience.source_id == document_id,
        ProfessionalExperience.is_reconciled.is_(False),
        ProfessionalExperience.reconciliation_status.in_(MUTABLE_RECONCILIATION_STATUSES),
    ).all()
    return _best_match(exp, rows, minimum=0.75)
