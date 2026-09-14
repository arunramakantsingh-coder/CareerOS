from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.intelligence.contracts import IntelligenceRequest
from app.intelligence.cv_ai_contract import CV_AI_INSTRUCTION, CV_AI_OUTPUT_SCHEMA
from app.intelligence.engine import engine
from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.career_fact_evidence import CareerFactEvidence
from app.models.document import Document
from app.models.extraction_result import ExtractionResult
from app.models.professional_experience import ProfessionalExperience


class AICVIngestionError(RuntimeError):
    pass


def ingest_cv_with_ai(document: Document, profile: CandidateProfile, db: Session) -> dict[str, Any]:
    if (document.document_category or "").lower() != "cv":
        raise AICVIngestionError("AI profile building is only supported for CV documents")

    text = (document.source_metadata or {}).get("extracted_text", "")
    if not isinstance(text, str) or not text.strip():
        raise AICVIngestionError("No extracted document text is available")
    text = _prepare_cv_text(text)

    request = IntelligenceRequest(
        task=CV_AI_INSTRUCTION,
        task_type="cv_extraction",
        context={"document": {"id": str(document.id), "filename": document.original_filename, "category": document.document_category, "text": text[:100000]}},
        output_schema=CV_AI_OUTPUT_SCHEMA,
        tools=[],
        temperature=0.0,
    )

    result = _run(request)
    if result.status != "completed":
        detail = result.result if isinstance(result.result, dict) else {"error": str(result.result)}
        raise AICVIngestionError(f"AI CV extraction failed: {detail}")

    payload = _parse(result.result)
    payload = _normalize_payload(payload)
    counts = _persist(document, profile, payload, db)

    extraction = ExtractionResult(
        candidate_id=profile.id,
        document_id=document.id,
        extraction_type="cv",
        extraction_version="3.0-ai-generic",
        extracted_data=payload,
        confidence_scores={"overall": 0.85},
        status="complete",
        is_reconciled=True,
        reconciled_at=datetime.utcnow(),
    )
    db.add(extraction)
    db.flush()

    metadata = dict(document.source_metadata or {})
    metadata["ai_profile_extraction"] = {
        "status": "completed",
        "contract_version": "3.0-generic-cv",
        "engine_version": result.engine_version,
        "provider": result.provider,
        "model": result.model,
        "trace_id": str(result.trace_id) if result.trace_id else None,
        "request_metrics": {
            "cv_text_chars": len(text),
            "instruction_chars": len(CV_AI_INSTRUCTION),
            "schema_chars": len(json.dumps(CV_AI_OUTPUT_SCHEMA, separators=(",", ":"))),
        },
        "counts": counts,
        "extraction_result_id": str(extraction.id),
    }
    document.source_metadata = metadata
    document.extraction_id = extraction.id
    document.extraction_status = "complete"
    document.processing_status = {**(document.processing_status or {}), "stage": "ai_reconciled"}
    document.processing_stage = "complete"
    document.status = "processed"
    profile.reconciliation_status = "complete" if counts["needs_review"] == 0 else "conflicting"
    db.commit()

    return {
        "status": profile.reconciliation_status,
        "document_id": str(document.id),
        "extraction_result_id": str(extraction.id),
        "model": result.model,
        "provider": result.provider,
        "trace_id": str(result.trace_id) if result.trace_id else None,
        "counts": counts,
    }


def _persist(document: Document, profile: CandidateProfile, payload: dict[str, Any], db: Session) -> dict[str, int]:
    profile_data = payload.get("profile") or {}
    mappings = {
        "full_name": profile_data.get("full_name"),
        "location": profile_data.get("location"),
        "title": profile_data.get("title"),
        "summary": profile_data.get("summary"),
        "primary_email": profile_data.get("email"),
        "primary_phone": profile_data.get("phone"),
        "linkedin_url": profile_data.get("linkedin"),
    }
    for field, value in mappings.items():
        if value not in (None, "") and getattr(profile, field, None) in (None, ""):
            setattr(profile, field, value)

    applied, needs_review = _apply_employment(document, profile, payload.get("employment") or [], db)

    skills = 0
    for value in payload.get("skills") or []:
        if _skill(document, profile, value, db):
            skills += 1

    certifications = 0
    for item in payload.get("certifications") or []:
        if _cert(document, profile, item, db):
            certifications += 1

    education = 0
    for item in payload.get("education") or []:
        if _edu(document, profile, item, db):
            education += 1

    projects = _merge_objects(profile.projects or [], payload.get("projects") or [], "name", str(document.id))
    accomplishments = _merge_objects(profile.accomplishments or [], payload.get("accomplishments") or [], "title", str(document.id))
    profile.projects = projects
    profile.accomplishments = accomplishments

    for item in projects:
        if item.get("source_document_id") == str(document.id):
            _evidence(profile.id, document, "project", item.get("id"), 0.85, item.get("description"), db)
    for item in accomplishments:
        if item.get("source_document_id") == str(document.id):
            _evidence(profile.id, document, "accomplishment", item.get("id"), 0.85, item.get("description"), db)

    return {
        "experiences": applied,
        "needs_review": needs_review,
        "skills": skills,
        "certifications": certifications,
        "education": education,
        "projects": len(projects),
        "accomplishments": len(accomplishments),
    }


def _apply_employment(document: Document, profile: CandidateProfile, incoming: list[Any], db: Session) -> tuple[int, int]:
    applied = 0
    needs_review = 0
    for item in incoming:
        if not isinstance(item, dict):
            continue
        employer = _clean(item.get("employer"))
        title = _clean(item.get("title"))
        if not employer or not title:
            needs_review += 1
            continue

        start_date = _date(item.get("start_date"))
        end_date = _date(item.get("end_date"))
        existing = (
            db.query(ProfessionalExperience)
            .filter(ProfessionalExperience.candidate_id == profile.id, ProfessionalExperience.company.ilike(employer), ProfessionalExperience.title.ilike(title))
            .all()
        )
        row = next((candidate for candidate in existing if _same_date(candidate.start_date, start_date) and _same_date(candidate.end_date, end_date)), None)
        if not row:
            row = ProfessionalExperience(
                candidate_id=profile.id,
                company=employer,
                client=_clean(item.get("client")),
                title=title,
                location=_clean(item.get("location")),
                start_date=start_date,
                end_date=end_date,
                is_current=end_date is None,
                responsibilities=item.get("responsibilities") or [],
                achievements=item.get("achievements") or [],
                technologies=item.get("technologies") or [],
                source_type="cv_ai",
                source_id=document.id,
                is_reconciled=True,
                reconciliation_status="reconciled",
            )
            db.add(row)
            db.flush()
        else:
            if not row.client and item.get("client"):
                row.client = _clean(item.get("client"))
            if not row.location and item.get("location"):
                row.location = _clean(item.get("location"))
            if not row.responsibilities and item.get("responsibilities"):
                row.responsibilities = item.get("responsibilities")
            if not row.achievements and item.get("achievements"):
                row.achievements = item.get("achievements")
            if not row.technologies and item.get("technologies"):
                row.technologies = item.get("technologies")

        _evidence(profile.id, document, "employment", row.id, 0.85, item.get("description"), db)
        applied += 1
    return applied, needs_review


def _skill(doc: Document, profile: CandidateProfile, value: Any, db: Session) -> bool:
    name = _clean(value)
    if not name:
        return False
    row = db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id, CandidateSkill.name.ilike(name)).first()
    if not row:
        row = CandidateSkill(candidate_id=profile.id, name=name, source_type="cv_ai", source_id=doc.id, confidence=0.85)
        db.add(row)
        db.flush()
    else:
        row.confidence = max(float(row.confidence or 0), 0.85)
    _evidence(profile.id, doc, "skill", row.id, 0.85, name, db)
    return True


def _cert(doc: Document, profile: CandidateProfile, item: dict[str, Any], db: Session) -> bool:
    name = _clean(item.get("name"))
    if not name:
        return False
    issuer = _clean(item.get("issuer"))
    row = db.query(CandidateCertification).filter(CandidateCertification.candidate_id == profile.id, CandidateCertification.name.ilike(name)).first()
    if not row:
        row = CandidateCertification(candidate_id=profile.id, name=name, issuer=issuer or "Unknown", source_type="cv_ai", source_id=doc.id, confidence=0.85)
        db.add(row)
        db.flush()
    else:
        if row.issuer == "Unknown" and issuer:
            row.issuer = issuer
        row.confidence = max(float(row.confidence or 0), 0.85)
    row.issue_date = row.issue_date or _date(item.get("issue_date"))
    row.expiry_date = row.expiry_date or _date(item.get("expiry_date"))
    row.credential_reference = row.credential_reference or _clean(item.get("credential_reference"))
    _evidence(profile.id, doc, "certification", row.id, 0.85, name, db)
    return True


def _edu(doc: Document, profile: CandidateProfile, item: dict[str, Any], db: Session) -> bool:
    institution = _clean(item.get("institution"))
    degree = _clean(item.get("degree"))
    if not institution or not degree:
        return False
    row = db.query(CandidateEducation).filter(CandidateEducation.candidate_id == profile.id, CandidateEducation.institution.ilike(institution), CandidateEducation.degree.ilike(degree)).first()
    if not row:
        row = CandidateEducation(candidate_id=profile.id, institution=institution, degree=degree, source_type="cv_ai", source_id=doc.id, confidence=0.85)
        db.add(row)
        db.flush()
    row.field_of_study = row.field_of_study or _clean(item.get("field_of_study"))
    row.start_date = row.start_date or _date(item.get("start_date"))
    row.end_date = row.end_date or _date(item.get("end_date"))
    row.grade = row.grade or _clean(item.get("grade"))
    row.confidence = max(float(row.confidence or 0), 0.85)
    _evidence(profile.id, doc, "education", row.id, 0.85, f"{degree} — {institution}", db)
    return True


def _merge_objects(existing: list[Any], incoming: list[Any], key_field: str, source_document_id: str) -> list[dict[str, Any]]:
    result = [dict(x) for x in existing if isinstance(x, dict)]
    seen = {_norm(x.get(key_field)) for x in result if x.get(key_field)}
    for item in incoming:
        if not isinstance(item, dict):
            continue
        key = _norm(item.get(key_field))
        if not key or key in seen:
            continue
        obj = dict(item)
        obj["id"] = str(uuid4())
        obj["source_document_id"] = source_document_id
        result.append(obj)
        seen.add(key)
    return result


def _evidence(candidate_id: Any, doc: Document, kind: str, fact_id: Any, confidence: float, excerpt: Any, db: Session) -> None:
    if not fact_id:
        return
    try:
        fact_uuid = UUID(str(fact_id))
    except (ValueError, TypeError):
        return
    row = db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id == candidate_id, CareerFactEvidence.document_id == doc.id, CareerFactEvidence.fact_type == kind, CareerFactEvidence.fact_id == fact_uuid).first()
    if row:
        row.confidence = max(row.confidence, confidence)
        row.excerpt = _clean(excerpt) or row.excerpt
        return
    db.add(CareerFactEvidence(candidate_id=candidate_id, document_id=doc.id, fact_type=kind, fact_id=fact_uuid, relationship="supports", confidence=confidence, excerpt=_clean(excerpt)))


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "profile": payload.get("profile") if isinstance(payload.get("profile"), dict) else {},
        "employment": payload.get("employment") if isinstance(payload.get("employment"), list) else [],
        "education": payload.get("education") if isinstance(payload.get("education"), list) else [],
        "certifications": payload.get("certifications") if isinstance(payload.get("certifications"), list) else [],
        "skills": payload.get("skills") if isinstance(payload.get("skills"), list) else [],
        "projects": payload.get("projects") if isinstance(payload.get("projects"), list) else [],
        "accomplishments": payload.get("accomplishments") if isinstance(payload.get("accomplishments"), list) else [],
    }
    result["skills"] = [x.strip() for x in result["skills"] if isinstance(x, str) and x.strip()]
    return result


def _prepare_cv_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def _norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def _clean(value: Any) -> str | None:
    return str(value).strip() if value not in (None, "") else None


def _same_date(left: datetime | None, right: datetime | None) -> bool:
    if left is None or right is None:
        return left is right
    return left.date() == right.date()


def _date(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%B %Y", "%b %Y", "%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _parse(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        raise AICVIngestionError("AI returned an invalid CV extraction payload")
    text = re.sub(r"^```(?:json)?\s*", "", value.strip(), flags=re.IGNORECASE)
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
