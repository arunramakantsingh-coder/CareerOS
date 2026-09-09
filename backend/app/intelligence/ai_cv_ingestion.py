from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.intelligence.contracts import IntelligenceRequest
from app.intelligence.engine import engine
from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.document import Document
from app.models.professional_experience import ProfessionalExperience


EMPLOYMENT_ITEM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "organization": {"type": "string", "minLength": 1, "maxLength": 255},
        "client": {"type": ["string", "null"], "maxLength": 255},
        "title": {"type": "string", "minLength": 1, "maxLength": 255},
        "start_date": {"type": ["string", "null"]},
        "end_date": {"type": ["string", "null"]},
        "is_current": {"type": "boolean"},
        "responsibilities": {"type": "array", "items": {"type": "string"}, "maxItems": 30},
        "achievements": {"type": "array", "items": {"type": "string"}, "maxItems": 20},
        "technologies": {"type": "array", "items": {"type": "string"}, "maxItems": 50},
        "industries": {"type": "array", "items": {"type": "string"}, "maxItems": 15},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": [
        "organization", "client", "title", "start_date", "end_date", "is_current",
        "responsibilities", "achievements", "technologies", "industries", "confidence",
    ],
}

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
                "years_experience": {"type": ["number", "null"]},
                "industries": {"type": "array", "items": {"type": "string"}, "maxItems": 20},
                "seniority": {"type": ["string", "null"]},
            },
            "required": [
                "full_name", "location", "title", "summary", "primary_email",
                "primary_phone", "linkedin_url", "years_experience", "industries", "seniority",
            ],
        },
        "experiences": {
            "type": "array",
            "maxItems": 30,
            "items": EMPLOYMENT_ITEM_SCHEMA,
        },
        "skills": {
            "type": "array",
            "maxItems": 100,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": ["string", "null"]},
                    "proficiency": {"type": ["string", "null"]},
                    "years_experience": {"type": ["number", "null"]},
                    "last_used": {"type": ["string", "null"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": [
                    "name", "category", "proficiency", "years_experience", "last_used", "confidence",
                ],
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
                    "credential_url": {"type": ["string", "null"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": [
                    "name", "issuer", "issue_date", "expiry_date", "credential_reference",
                    "credential_url", "confidence",
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
                    "is_current": {"type": "boolean"},
                    "grade": {"type": ["string", "null"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": [
                    "institution", "degree", "field_of_study", "start_date", "end_date",
                    "is_current", "grade", "confidence",
                ],
            },
        },
    },
    "required": ["profile", "experiences", "skills", "certifications", "education"],
}


class AICVIngestionError(RuntimeError):
    pass


def ingest_cv_with_ai(document: Document, profile: CandidateProfile, db: Session) -> dict[str, Any]:
    """Build the professional profile from one CV using the local/provider-neutral AI engine."""
    if (document.document_category or "").lower() != "cv":
        raise AICVIngestionError("Profile AI ingestion only accepts CV documents")

    text = (document.source_metadata or {}).get("extracted_text", "")
    if not isinstance(text, str) or not text.strip():
        raise AICVIngestionError("No extracted CV text is available")

    task = """
Read the complete CV and build the candidate's professional profile.

This is PROFILE BUILDING, not document reconciliation and not persona generation.
The CV is the primary source. Understand the document semantically even when PDF text is
flattened, reordered, or section headings are imperfect.

Extract every real employment role. Multiple roles at the same employer must remain separate.
For each employment role capture employer, optional client, title, dates, current status,
responsibilities, achievements, technologies, industries, and confidence.

Extract only information that is actually supported by the CV. Do not invent facts.
Do not create jobs from skills, technologies, competencies, certifications, education,
projects, summary text, or generic phrases.

Also extract the candidate identity/profile, skills, certifications, and education.
Do NOT generate personas. Personas are built later from the completed profile.

Return JSON only matching the supplied schema.
""".strip()

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
        raise AICVIngestionError(f"AI profile extraction failed: {detail}")

    payload = _parse(result.result)
    counts = _persist_profile(document, profile, payload, db)
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


def _persist_profile(
    document: Document,
    profile: CandidateProfile,
    payload: dict[str, Any],
    db: Session,
) -> dict[str, int]:
    values = payload.get("profile") or {}
    for field in (
        "full_name", "location", "title", "summary", "primary_email", "primary_phone",
        "linkedin_url", "years_experience", "seniority",
    ):
        value = values.get(field)
        if value not in (None, "", []):
            setattr(profile, field, value)

    profile.industries = _merge_strings(profile.industries or [], values.get("industries") or [])

    experiences = [_normalize_experience(item) for item in payload.get("experiences", []) if isinstance(item, dict)]
    experience_counts = _upsert_experiences(profile.id, document, experiences, db)

    skill_count = sum(_upsert_skill(profile, document, item, db) for item in payload.get("skills", []) if isinstance(item, dict))
    certification_count = sum(_upsert_certification(profile, document, item, db) for item in payload.get("certifications", []) if isinstance(item, dict))
    education_count = sum(_upsert_education(profile, document, item, db) for item in payload.get("education", []) if isinstance(item, dict))

    return {
        "experiences": experience_counts["written"],
        "needs_review": experience_counts["needs_review"],
        "skills": skill_count,
        "certifications": certification_count,
        "education": education_count,
    }


def _upsert_experiences(candidate_id, document: Document, experiences: list[dict[str, Any]], db: Session) -> dict[str, int]:
    written = 0
    needs_review = 0
    for exp in experiences:
        confidence = float(exp.get("confidence") or 0.0)
        target = (
            db.query(ProfessionalExperience)
            .filter(
                ProfessionalExperience.candidate_id == candidate_id,
                ProfessionalExperience.source_id == document.id,
                ProfessionalExperience.company.ilike(exp["organization"]),
                ProfessionalExperience.title.ilike(exp["title"]),
            )
            .first()
        )
        if target is None:
            target = _find_existing_profile_experience(candidate_id, exp, db)
        if target is None:
            target = ProfessionalExperience(candidate_id=candidate_id)
            db.add(target)

        if target.reconciliation_status == "user_confirmed":
            continue

        target.company = exp["organization"]
        target.client = exp.get("client")
        target.title = exp["title"]
        target.start_date = _parse_date(exp.get("start_date"))
        target.end_date = _parse_date(exp.get("end_date"))
        target.is_current = bool(exp.get("is_current"))
        target.responsibilities = exp.get("responsibilities") or []
        target.achievements = exp.get("achievements") or []
        target.technologies = exp.get("technologies") or []
        target.industries = exp.get("industries") or []
        target.industry = target.industries[0] if target.industries else None
        target.source_type = "cv_ai"
        target.source_id = document.id
        target.is_reconciled = confidence >= 0.85
        target.reconciliation_status = "ai_reconciled" if confidence >= 0.85 else "ai_review"
        db.flush()
        written += 1
        needs_review += int(confidence < 0.85)
    return {"written": written, "needs_review": needs_review}


def _find_existing_profile_experience(candidate_id, exp: dict[str, Any], db: Session):
    rows = (
        db.query(ProfessionalExperience)
        .filter(
            ProfessionalExperience.candidate_id == candidate_id,
            ProfessionalExperience.company.ilike(exp["organization"]),
            ProfessionalExperience.title.ilike(exp["title"]),
        )
        .all()
    )
    for row in rows:
        if row.reconciliation_status == "user_confirmed":
            continue
        if _same_month(row.start_date, exp.get("start_date")) and _same_month(row.end_date, exp.get("end_date")):
            return row
    return None


def _upsert_skill(profile: CandidateProfile, document: Document, item: dict[str, Any], db: Session) -> int:
    name = _clean(item.get("name"))
    if not name:
        return 0
    row = db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id, CandidateSkill.name.ilike(name)).first()
    if row is None:
        row = CandidateSkill(candidate_id=profile.id, name=name, source_type="cv_ai", source_id=document.id)
        db.add(row)
    row.category = row.category or _clean(item.get("category"))
    row.proficiency = row.proficiency or _clean(item.get("proficiency"))
    row.years_experience = row.years_experience or item.get("years_experience")
    row.last_used = row.last_used or _clean(item.get("last_used"))
    row.confidence = max(float(row.confidence or 0.0), float(item.get("confidence") or 0.0))
    db.flush()
    return 1


def _upsert_certification(profile: CandidateProfile, document: Document, item: dict[str, Any], db: Session) -> int:
    name = _clean(item.get("name"))
    if not name:
        return 0
    row = db.query(CandidateCertification).filter(CandidateCertification.candidate_id == profile.id, CandidateCertification.name.ilike(name)).first()
    if row is None:
        row = CandidateCertification(candidate_id=profile.id, name=name, issuer=_clean(item.get("issuer")), source_type="cv_ai", source_id=document.id)
        db.add(row)
    row.issuer = row.issuer or _clean(item.get("issuer"))
    row.issue_date = row.issue_date or _parse_date(item.get("issue_date"))
    row.expiry_date = row.expiry_date or _parse_date(item.get("expiry_date"))
    row.credential_reference = row.credential_reference or _clean(item.get("credential_reference"))
    row.credential_url = row.credential_url or _clean(item.get("credential_url"))
    row.confidence = max(float(row.confidence or 0.0), float(item.get("confidence") or 0.0))
    db.flush()
    return 1


def _upsert_education(profile: CandidateProfile, document: Document, item: dict[str, Any], db: Session) -> int:
    institution = _clean(item.get("institution"))
    degree = _clean(item.get("degree"))
    if not institution or not degree:
        return 0
    row = (
        db.query(CandidateEducation)
        .filter(
            CandidateEducation.candidate_id == profile.id,
            CandidateEducation.institution.ilike(institution),
            CandidateEducation.degree.ilike(degree),
        )
        .first()
    )
    if row is None:
        row = CandidateEducation(candidate_id=profile.id, institution=institution, degree=degree, source_type="cv_ai", source_id=document.id)
        db.add(row)
    row.field_of_study = row.field_of_study or _clean(item.get("field_of_study"))
    row.start_date = row.start_date or _parse_date(item.get("start_date"))
    row.end_date = row.end_date or _parse_date(item.get("end_date"))
    row.grade = row.grade or _clean(item.get("grade"))
    row.confidence = max(float(row.confidence or 0.0), float(item.get("confidence") or 0.0))
    db.flush()
    return 1


def _normalize_experience(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "organization": _clean(item.get("organization")) or "Unknown organization",
        "client": _clean(item.get("client")),
        "title": _clean(item.get("title")) or "Unknown title",
        "start_date": _clean(item.get("start_date")),
        "end_date": _clean(item.get("end_date")),
        "is_current": bool(item.get("is_current")),
        "responsibilities": _string_list(item.get("responsibilities"), 30),
        "achievements": _string_list(item.get("achievements"), 20),
        "technologies": _string_list(item.get("technologies"), 50),
        "industries": _string_list(item.get("industries"), 15),
        "confidence": max(0.0, min(1.0, float(item.get("confidence") or 0.0))),
    }


def _string_list(value: Any, maximum: int) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = _clean(item)
        if not text:
            continue
        key = re.sub(r"\s+", " ", text.lower()).strip()
        if key in seen:
            continue
        seen.add(key)
        result.append(text[:1000])
        if len(result) >= maximum:
            break
    return result


def _merge_strings(existing: list[str], incoming: list[str]) -> list[str]:
    result = list(existing)
    seen = {re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip() for value in result}
    for value in incoming:
        text = _clean(value)
        if not text:
            continue
        key = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
        if key not in seen:
            result.append(text)
            seen.add(key)
    return result


def _same_month(value: Any, other: Any) -> bool:
    if not value or not other:
        return value is None and other is None
    parsed = _parse_date(other)
    return parsed is not None and value.strftime("%Y-%m") == parsed.strftime("%Y-%m")


def _parse_date(value: Any):
    if not value or not isinstance(value, str):
        return None
    cleaned = value.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%B %Y", "%b %Y", "%Y"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def _clean(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value).strip() or None


def _parse(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        raise AICVIngestionError("Local AI returned an invalid profile payload")
    cleaned = value.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise AICVIngestionError(f"Local AI returned invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise AICVIngestionError("Local AI returned a non-object profile payload")
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
