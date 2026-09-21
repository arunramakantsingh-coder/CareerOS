from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.intelligence.contracts import IntelligenceRequest
from app.intelligence.engine import engine
from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.career_fact_evidence import CareerFactEvidence
from app.models.document import Document
from app.models.professional_experience import ProfessionalExperience


SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "display_name": {"type": "string"},
        "category": {"type": "string", "enum": ["cv", "employment", "education", "certification", "achievement", "project", "reference", "other"]},
        "subcategory": {"type": "string"},
        "issuer": {"type": ["string", "null"]},
        "issue_date": {"type": ["string", "null"]},
        "expiry_date": {"type": ["string", "null"]},
        "document_number": {"type": ["string", "null"]},
        "summary": {"type": "string"},
        "evidence_state": {"type": "string", "enum": ["supporting", "reported_only", "needs_review", "unrelated"]},
        "matches": {
            "type": "array",
            "maxItems": 20,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "fact_type": {"type": "string", "enum": ["employment", "education", "certification", "skill", "project", "accomplishment"]},
                    "fact_id": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "relationship": {"type": "string", "enum": ["supports", "partially_supports", "conflicts"]},
                    "excerpt": {"type": ["string", "null"]},
                },
                "required": ["fact_type", "fact_id", "confidence", "relationship", "excerpt"],
            },
        },
    },
    "required": ["display_name", "category", "subcategory", "issuer", "issue_date", "expiry_date", "document_number", "summary", "evidence_state", "matches"],
}


class DocumentEnrichmentError(RuntimeError):
    pass


def enrich_document(document: Document, profile: CandidateProfile, db: Session) -> dict[str, Any]:
    text = (document.source_metadata or {}).get("extracted_text", "")
    if not isinstance(text, str) or not text.strip():
        raise DocumentEnrichmentError("No extracted text is available for AI document understanding")

    facts = {
        "employment": [
            {"id": str(x.id), "title": x.title, "company": x.company, "client": getattr(x, "client", None), "start": str(x.start_date), "end": str(x.end_date)}
            for x in db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == profile.id).all()
        ],
        "education": [
            {"id": str(x.id), "institution": x.institution, "degree": x.degree, "field": x.field_of_study}
            for x in db.query(CandidateEducation).filter(CandidateEducation.candidate_id == profile.id).all()
        ],
        "certification": [
            {"id": str(x.id), "name": x.name, "issuer": x.issuer, "credential": x.credential_reference}
            for x in db.query(CandidateCertification).filter(CandidateCertification.candidate_id == profile.id).all()
        ],
        "skill": [
            {"id": str(x.id), "name": x.name, "category": x.category}
            for x in db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id).all()
        ],
        "project": profile.projects or [],
        "accomplishment": profile.accomplishments or [],
    }

    task = """Understand this professional document and decide what career fact(s) it actually supports.

Rules:
- The document content is the source of truth; never invent a credential, employer, date, issuer, project or achievement.
- Classify the document by its content, not its filename.
- Generate a short human-friendly display_name describing the document. Never include the original filename in display_name.
- Prefer a dedicated supporting document over a CV when determining evidence_state.
- Match only against the supplied existing CareerOS fact IDs. Never fabricate IDs.
- A CV can support reported career facts, but a CV is not a dedicated certificate, degree, employment letter or award.
- For an unrelated document, return no matches.
"""
    request = IntelligenceRequest(
        task=task,
        context={
            "document": {"id": str(document.id), "filename": document.original_filename, "deterministic_category": document.document_category, "text": text[:100000]},
            "existing_profile_facts": facts,
        },
        output_schema=SCHEMA,
        tools=[],
        temperature=0.0,
    )
    result = _run(request)
    if result.status != "completed":
        raise DocumentEnrichmentError(f"AI document understanding failed: {result.result}")
    payload = _parse(result.result)

    document.user_label = _clean(payload.get("display_name")) or _fallback_name(document, payload)
    document.document_category = payload.get("category") or document.document_category
    document.document_subcategory = _clean(payload.get("subcategory")) or document.document_subcategory
    document.document_type = document.document_subcategory
    document.detected_type = f"{document.document_category}:{document.document_subcategory or 'unknown'}"
    document.issuer = _clean(payload.get("issuer")) or document.issuer
    document.issue_date = document.issue_date or _date(payload.get("issue_date"))
    document.expiry_date = document.expiry_date or _date(payload.get("expiry_date"))
    document.document_number = document.document_number or _clean(payload.get("document_number"))
    document.classification_confidence = max(float(document.classification_confidence or 0), _best_match_confidence(payload))
    document.classification_reason = _clean(payload.get("summary"))
    document.verification_status = "verified" if payload.get("evidence_state") == "supporting" else "needs_confirmation" if payload.get("evidence_state") == "needs_review" else "reported"
    document.processing_stage = "ai_enriched"
    document.status = "processed"
    metadata = dict(document.source_metadata or {})
    metadata["ai_document_enrichment"] = {
        "status": "completed",
        "provider": result.provider,
        "model": result.model,
        "trace_id": str(result.trace_id) if result.trace_id else None,
        "summary": payload.get("summary"),
        "evidence_state": payload.get("evidence_state"),
        "matches": payload.get("matches") or [],
    }
    document.source_metadata = metadata

    valid_ids = {kind: {str(item["id"]) for item in rows} for kind, rows in facts.items()}
    linked = 0
    for match in payload.get("matches") or []:
        if not isinstance(match, dict):
            continue
        fact_type = str(match.get("fact_type") or "")
        fact_id = str(match.get("fact_id") or "")
        confidence = float(match.get("confidence") or 0)
        if fact_type not in valid_ids or fact_id not in valid_ids[fact_type] or confidence < 0.70:
            continue
        existing = db.query(CareerFactEvidence).filter(
            CareerFactEvidence.candidate_id == profile.id,
            CareerFactEvidence.document_id == document.id,
            CareerFactEvidence.fact_type == fact_type,
            CareerFactEvidence.fact_id == UUID(fact_id),
        ).first()
        if existing:
            existing.confidence = max(existing.confidence, confidence)
            existing.relationship = match.get("relationship") or existing.relationship
            existing.excerpt = _clean(match.get("excerpt")) or existing.excerpt
        else:
            db.add(CareerFactEvidence(
                candidate_id=profile.id,
                document_id=document.id,
                fact_type=fact_type,
                fact_id=UUID(fact_id),
                relationship=match.get("relationship") or "supports",
                confidence=confidence,
                excerpt=_clean(match.get("excerpt")),
            ))
        linked += 1

    # Rename the stored presentation filename using AI meaning while retaining
    # original_filename internally for audit/traceability.
    old_path = Path(document.storage_path)
    safe = _safe_filename(document.user_label or document.detected_type or "career-document")
    suffix = old_path.suffix.lower()
    new_name = f"{safe}{suffix}"
    new_path = old_path.with_name(new_name)
    if new_path != old_path and old_path.exists():
        if not new_path.exists():
            old_path.rename(new_path)
            document.storage_path = str(new_path)
            document.filename = new_name

    db.flush()
    return {"linked_facts": linked, "evidence_state": payload.get("evidence_state"), "display_name": document.user_label}


def _run(request: IntelligenceRequest):
    try:
        return asyncio.run(engine.execute(request))
    except RuntimeError as exc:
        if "asyncio.run() cannot be called" not in str(exc):
            raise
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(engine.execute(request))
        finally:
            loop.close()


def _parse(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        raise DocumentEnrichmentError("AI returned an invalid document payload")
    text = re.sub(r"^```(?:json)?\s*", "", value.strip(), flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DocumentEnrichmentError(f"AI returned invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise DocumentEnrichmentError("AI document result must be an object")
    return parsed


def _clean(value: Any) -> str | None:
    return str(value).strip() if value not in (None, "") else None


def _date(value: Any):
    from datetime import datetime
    if not isinstance(value, str) or not value.strip():
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%B %Y", "%b %Y", "%Y"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            pass
    return None


def _best_match_confidence(payload: dict[str, Any]) -> float:
    values = [float(x.get("confidence") or 0) for x in payload.get("matches") or [] if isinstance(x, dict)]
    return max(values, default=0.0)


def _fallback_name(document: Document, payload: dict[str, Any]) -> str:
    issuer = _clean(payload.get("issuer"))
    subtype = _clean(payload.get("subcategory")) or "Professional Document"
    return f"{subtype.title()} — {issuer}" if issuer else subtype.title()


def _safe_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._ -]+", "", value).strip(" .")
    value = re.sub(r"\s+", " ", value)
    return value[:180] or "Career Document"
