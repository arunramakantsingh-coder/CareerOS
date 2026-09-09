from __future__ import annotations

import re
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.career_fact_evidence import CareerFactEvidence
from app.models.document import Document
from app.models.professional_experience import ProfessionalExperience


STOP_WORDS = {
    "about", "what", "with", "from", "that", "this", "have", "has", "and", "the", "for", "into", "your", "my",
    "career", "professional", "experience", "profile", "work", "skills", "years", "tell", "show", "give", "me",
}


def _tokens(value: str) -> set[str]:
    words = re.findall(r"[a-z0-9][a-z0-9+#./-]{1,}", (value or "").lower())
    return {word for word in words if word not in STOP_WORDS and len(word) > 1}


def _score(query_tokens: set[str], text: str) -> float:
    candidate = _tokens(text)
    if not query_tokens or not candidate:
        return 0.0
    overlap = query_tokens & candidate
    if not overlap:
        return 0.0
    return round(min(0.99, len(overlap) / max(1, len(query_tokens)) * 0.85 + 0.15), 3)


def _excerpt(text: str, query_tokens: set[str], limit: int = 600) -> str:
    compact = re.sub(r"\s+", " ", (text or "")).strip()
    if len(compact) <= limit:
        return compact
    lowered = compact.lower()
    for token in sorted(query_tokens, key=len, reverse=True):
        idx = lowered.find(token.lower())
        if idx >= 0:
            start = max(0, idx - 180)
            end = min(len(compact), start + limit)
            prefix = "…" if start else ""
            suffix = "…" if end < len(compact) else ""
            return prefix + compact[start:end] + suffix
    return compact[:limit] + "…"


def retrieve_career_knowledge(db: Session, user_id: UUID, query: str, top_k: int = 8, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    """Tenant-scoped lexical retrieval over canonical identity facts and evidence.

    This is the deterministic retrieval baseline. It intentionally has no embedding/vector
    dependency yet; the result contract is designed so vector/hybrid ranking can replace
    this implementation later without changing Intelligence Engine callers.
    """
    query_tokens = _tokens(query)
    if not query_tokens:
        return {"query": query, "results": [], "retrieval_ready": True, "retrieval_mode": "lexical"}

    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == user_id,
        CandidateProfile.is_active.is_(True),
    ).first()
    if not profile:
        return {"query": query, "results": [], "retrieval_ready": True, "retrieval_mode": "lexical"}

    filters = filters or {}
    allowed_types = set(filters.get("fact_types", []))
    candidates: list[dict[str, Any]] = []

    profile_text = " | ".join(str(value) for value in (
        profile.full_name, profile.title, profile.summary, profile.location, profile.seniority,
        profile.years_experience, profile.industries,
    ) if value)
    _append(candidates, _score(query_tokens, profile_text), "profile", profile.id, profile_text, None, None, 0.82, "INFERRED", query_tokens, allowed_types)

    for item in db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == profile.id).all():
        text = " | ".join(str(value) for value in (item.company, item.title, item.location, item.industry, item.responsibilities, item.achievements) if value)
        _append(candidates, _score(query_tokens, text), "employment", item.id, text, item.source_id, "employment", 0.8, "EXTRACTED", query_tokens, allowed_types)

    for item in db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id).all():
        text = " | ".join(str(value) for value in (item.name, item.category, item.proficiency, item.years_experience) if value)
        _append(candidates, _score(query_tokens, text), "skill", item.id, text, item.source_id, "skill", item.confidence or 0.82, "EXTRACTED", query_tokens, allowed_types)

    for item in db.query(CandidateCertification).filter(CandidateCertification.candidate_id == profile.id).all():
        text = " | ".join(str(value) for value in (item.name, item.issuer, item.credential_reference, item.issue_date, item.expiry_date) if value)
        _append(candidates, _score(query_tokens, text), "certification", item.id, text, item.source_id, "certification", item.confidence or 0.88, "EXTRACTED", query_tokens, allowed_types)

    for item in db.query(CandidateEducation).filter(CandidateEducation.candidate_id == profile.id).all():
        text = " | ".join(str(value) for value in (item.institution, item.degree, item.field_of_study, item.start_date, item.end_date) if value)
        _append(candidates, _score(query_tokens, text), "education", item.id, text, item.source_id, "education", item.confidence or 0.9, "EXTRACTED", query_tokens, allowed_types)

    for item in db.query(Document).filter(Document.candidate_id == profile.id).all():
        metadata = item.source_metadata or {}
        representation = metadata.get("representation") if isinstance(metadata, dict) else None
        if isinstance(representation, dict):
            document_text = representation.get("markdown") or representation.get("text") or ""
        else:
            document_text = metadata.get("extracted_text", "") if isinstance(metadata, dict) else ""
        text = " | ".join(str(value) for value in (item.original_filename, item.document_category, item.document_subcategory, item.issuer, item.user_label, document_text) if value)
        _append(candidates, _score(query_tokens, text), "document", item.id, text, item.id, "document", item.classification_confidence or 0.7, "EXTRACTED", query_tokens, allowed_types)

    for evidence in db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id == profile.id).all():
        text = evidence.excerpt or ""
        _append(candidates, _score(query_tokens, text), evidence.fact_type, evidence.fact_id, text, evidence.document_id, evidence.fact_type, evidence.confidence, "EXTRACTED", query_tokens, allowed_types)

    candidates.sort(key=lambda item: (item["score"], item["confidence"]), reverse=True)
    return {
        "query": query,
        "results": candidates[:top_k],
        "retrieval_ready": True,
        "retrieval_mode": "lexical",
        "tenant_scoped": True,
        "candidate_id": str(profile.id),
    }


def _append(target: list[dict[str, Any]], score: float, result_type: str, fact_id: UUID, text: str, document_id: UUID | None, fact_type: str | None, confidence: float, trust_state: str, query_tokens: set[str], allowed_types: set[str]) -> None:
    if not score or (allowed_types and result_type not in allowed_types and (fact_type or "") not in allowed_types):
        return
    target.append({
        "score": score,
        "type": result_type,
        "title": result_type.replace("_", " ").title(),
        "content": _excerpt(text, query_tokens),
        "evidence": {
            "document_id": str(document_id) if document_id else None,
            "fact_type": fact_type,
            "fact_id": str(fact_id) if fact_id else None,
            "excerpt": _excerpt(text, query_tokens),
            "confidence": confidence,
            "trust_state": trust_state,
        },
    })
