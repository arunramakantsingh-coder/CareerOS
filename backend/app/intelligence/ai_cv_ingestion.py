from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.intelligence.contracts import IntelligenceRequest
from app.intelligence.engine import engine
from app.intelligence.identity_reconciliation import EMPLOYMENT_SCHEMA, _apply_experiences, _sanitize_experience
from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.career_fact_evidence import CareerFactEvidence
from app.models.document import Document


# Deliberately small AI-facing contract. It describes the information we want
# extracted from a CV, not CareerOS database models or persistence rules.
SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "profile": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "full_name": {"type": ["string", "null"]},
                "location": {"type": ["string", "null"]},
                "title": {"type": ["string", "null"]},
                "summary": {"type": ["string", "null"]},
                "primary_email": {"type": ["string", "null"]},
                "primary_phone": {"type": ["string", "null"]},
                "linkedin_url": {"type": ["string", "null"]},
                "industries": {"type": "array", "items": {"type": "string"}, "maxItems": 20},
            },
            "required": [
                "full_name",
                "location",
                "title",
                "summary",
                "primary_email",
                "primary_phone",
                "linkedin_url",
                "industries",
            ],
        },
        "experiences": EMPLOYMENT_SCHEMA["properties"]["experiences"],
        "skills": {
            "type": "array",
            "maxItems": 100,
            "items": {
                "type": "string",
            },
        },
        "certifications": {
            "type": "array",
            "maxItems": 50,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "issuer": {"type": ["string", "null"]},
                    "issue_date": {"type": ["string", "null"]},
                    "expiry_date": {"type": ["string", "null"]},
                    "credential_reference": {"type": ["string", "null"]},
                },
                "required": [
                    "name",
                    "issuer",
                    "issue_date",
                    "expiry_date",
                    "credential_reference",
                ],
            },
        },
        "education": {
            "type": "array",
            "maxItems": 20,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "institution": {"type": "string"},
                    "degree": {"type": "string"},
                    "field_of_study": {"type": ["string", "null"]},
                    "start_date": {"type": ["string", "null"]},
                    "end_date": {"type": ["string", "null"]},
                    "grade": {"type": ["string", "null"]},
                },
                "required": [
                    "institution",
                    "degree",
                    "field_of_study",
                    "start_date",
                    "end_date",
                    "grade",
                ],
            },
        },
    },
    "required": ["profile", "experiences", "skills", "certifications", "education"],
}


class AICVIngestionError(RuntimeError):
    pass


def ingest_cv_with_ai(document: Document, profile: CandidateProfile, db: Session) -> dict[str, Any]:
    if (document.document_category or "").lower() != "cv":
        raise AICVIngestionError("AI profile building is only supported for CV documents")

    text = (document.source_metadata or {}).get("extracted_text", "")
    if not isinstance(text, str) or not text.strip():
        raise AICVIngestionError("No extracted document text is available")

    task = """Extract a professional profile from the supplied CV.

Return only the requested structured information.

Rules:
- Read the supplied CV as the source of truth.
- Extract what is explicitly present; do not invent or infer facts.
- Keep every genuine employment role as a separate experience, including multiple roles at one employer.
- Preserve employer, optional client, title and dates from the CV.
- Do not turn skills, technologies, projects, certifications, education, summary text or generic phrases into jobs.
- Extract skills as simple names only.
- Extract certifications and education only when stated in the CV.
- Use null or an empty array when the CV does not provide a value.
- Do not generate personas, recommendations, evidence graphs or database fields.
"""

    request = IntelligenceRequest(
        task=task,
        context={
            "document": {
                "id": str(document.id),
                "filename": document.original_filename,
                "category": document.document_category,
                "text": text[:100000],
            }
        },
        output_schema=SCHEMA,
        tools=[],
        temperature=0.0,
    )

    result = _run(request)
    if result.status != "completed":
        detail = result.result if isinstance(result.result, dict) else {"error": str(result.result)}
        raise AICVIngestionError(f"AI CV extraction failed: {detail}")

    payload = _parse(result.result)
    counts = _persist(document, profile, payload, db)
    metadata = dict(document.source_metadata or {})
    metadata["ai_profile_extraction"] = {
        "status": "completed",
        "engine_version": result.engine_version,
        "provider": result.provider,
        "model": result.model,
        "trace_id": str(result.trace_id) if result.trace_id else None,
        "counts": counts,
    }
    document.source_metadata = metadata
    profile.reconciliation_status = "complete" if counts["needs_review"] == 0 else "conflicting"
    db.commit()

    return {
        "status": profile.reconciliation_status,
        "document_id": str(document.id),
        "model": result.model,
        "provider": result.provider,
        "trace_id": str(result.trace_id) if result.trace_id else None,
        "counts": counts,
    }


def _persist(document: Document, profile: CandidateProfile, payload: dict[str, Any], db: Session) -> dict[str, int]:
    profile_data = payload.get("profile") or {}
    for field in (
        "full_name",
        "location",
        "title",
        "summary",
        "primary_email",
        "primary_phone",
        "linkedin_url",
    ):
        value = profile_data.get(field)
        if value not in (None, "", []) and getattr(profile, field, None) in (None, ""):
            setattr(profile, field, value)

    profile.industries = _merge(profile.industries or [], profile_data.get("industries") or [])

    raw_experiences = [
        _sanitize_experience(item)
        for item in payload.get("experiences", [])
        if isinstance(item, dict)
    ]
    applied, review, protected = _apply_experiences(document, raw_experiences, db)

    for skill_name in payload.get("skills", []):
        _skill(document, profile, skill_name, db)
    for item in payload.get("certifications", []):
        _cert(document, profile, item, db)
    for item in payload.get("education", []):
        _edu(document, profile, item, db)

    return {
        "experiences": len(applied),
        "needs_review": len(review),
        "protected": len(protected),
        "skills": len(payload.get("skills", [])),
        "certifications": len(payload.get("certifications", [])),
        "education": len(payload.get("education", [])),
    }


def _skill(doc: Document, profile: CandidateProfile, skill_name: Any, db: Session) -> None:
    name = _clean(skill_name)
    if not name:
        return

    row = (
        db.query(CandidateSkill)
        .filter(CandidateSkill.candidate_id == profile.id, CandidateSkill.name.ilike(name))
        .first()
    )
    if not row:
        row = CandidateSkill(
            candidate_id=profile.id,
            name=name,
            source_type="cv_ai",
            source_id=doc.id,
        )
        db.add(row)
    row.confidence = max(float(row.confidence or 0), 0.85)
    db.flush()
    _evidence(profile.id, doc, "skill", row.id, 0.85, None, db)


def _cert(doc: Document, profile: CandidateProfile, item: dict[str, Any], db: Session) -> None:
    name = _clean(item.get("name"))
    issuer = _clean(item.get("issuer")) or "Unknown"
    if not name:
        return

    row = (
        db.query(CandidateCertification)
        .filter(CandidateCertification.candidate_id == profile.id, CandidateCertification.name.ilike(name))
        .first()
    )
    if not row:
        row = CandidateCertification(
            candidate_id=profile.id,
            name=name,
            issuer=issuer,
            source_type="cv_ai",
            source_id=doc.id,
        )
        db.add(row)

    row.issuer = row.issuer if row.issuer != "Unknown" else issuer
    row.issue_date = row.issue_date or _date(item.get("issue_date"))
    row.expiry_date = row.expiry_date or _date(item.get("expiry_date"))
    row.credential_reference = row.credential_reference or _clean(item.get("credential_reference"))
    row.confidence = max(float(row.confidence or 0), 0.85)
    db.flush()
    _evidence(profile.id, doc, "certification", row.id, 0.85, None, db)


def _edu(doc: Document, profile: CandidateProfile, item: dict[str, Any], db: Session) -> None:
    institution = _clean(item.get("institution"))
    degree = _clean(item.get("degree"))
    if not institution or not degree:
        return

    row = (
        db.query(CandidateEducation)
        .filter(
            CandidateEducation.candidate_id == profile.id,
            CandidateEducation.institution.ilike(institution),
            CandidateEducation.degree.ilike(degree),
        )
        .first()
    )
    if not row:
        row = CandidateEducation(
            candidate_id=profile.id,
            institution=institution,
            degree=degree,
            source_type="cv_ai",
            source_id=doc.id,
        )
        db.add(row)

    row.field_of_study = row.field_of_study or _clean(item.get("field_of_study"))
    row.start_date = row.start_date or _date(item.get("start_date"))
    row.end_date = row.end_date or _date(item.get("end_date"))
    row.grade = row.grade or _clean(item.get("grade"))
    row.confidence = max(float(row.confidence or 0), 0.85)
    db.flush()
    _evidence(profile.id, doc, "education", row.id, 0.85, None, db)


def _evidence(
    candidate_id: Any,
    doc: Document,
    kind: str,
    fact_id: Any,
    confidence: float,
    excerpt: Any,
    db: Session,
) -> None:
    row = (
        db.query(CareerFactEvidence)
        .filter(
            CareerFactEvidence.candidate_id == candidate_id,
            CareerFactEvidence.document_id == doc.id,
            CareerFactEvidence.fact_type == kind,
            CareerFactEvidence.fact_id == fact_id,
        )
        .first()
    )
    if row:
        row.confidence = max(row.confidence, confidence)
        row.excerpt = _clean(excerpt) or row.excerpt
        return

    db.add(
        CareerFactEvidence(
            candidate_id=candidate_id,
            document_id=doc.id,
            fact_type=kind,
            fact_id=fact_id,
            relationship="supports",
            confidence=confidence,
            excerpt=_clean(excerpt),
        )
    )


def _merge(existing: list[str], incoming: list[str]) -> list[str]:
    result = list(existing)
    seen = {_norm(x) for x in result}
    for value in incoming:
        if isinstance(value, str) and value.strip():
            key = _norm(value)
            if key not in seen:
                result.append(value.strip())
                seen.add(key)
    return result


def _norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def _clean(value: Any) -> str | None:
    return str(value).strip() if value not in (None, "") else None


def _date(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%B %Y", "%b %Y", "%Y"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    return None


def _parse(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        raise AICVIngestionError("AI returned an invalid CV extraction payload")

    text = value.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AICVIngestionError(f"AI returned invalid JSON: {exc}") from exc

    if not isinstance(parsed, dict):
        raise AICVIngestionError("AI CV extraction result must be a JSON object")
    return parsed


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
