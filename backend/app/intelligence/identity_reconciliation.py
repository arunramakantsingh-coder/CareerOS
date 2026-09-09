from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.intelligence.contracts import IntelligenceRequest
from app.intelligence.engine import engine
from app.models.career_fact_evidence import CareerFactEvidence
from app.models.document import Document
from app.models.professional_experience import ProfessionalExperience
from app.utils.cv_parser import CVParser


EMPLOYMENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "experiences": {
            "type": "array",
            "maxItems": 30,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "organization": {"type": "string"},
                    "client": {"type": ["string", "null"]},
                    "title": {"type": "string"},
                    "start_date": {"type": ["string", "null"]},
                    "end_date": {"type": ["string", "null"]},
                    "is_current": {"type": "boolean"},
                    "responsibilities": {"type": "array", "items": {"type": "string"}, "maxItems": 20},
                    "achievements": {"type": "array", "items": {"type": "string"}, "maxItems": 20},
                    "technologies": {"type": "array", "items": {"type": "string"}, "maxItems": 40},
                    "industries": {"type": "array", "items": {"type": "string"}, "maxItems": 10},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "evidence_excerpt": {"type": ["string", "null"]},
                },
                "required": [
                    "organization", "client", "title", "start_date", "end_date", "is_current",
                    "responsibilities", "achievements", "technologies", "industries", "confidence", "evidence_excerpt",
                ],
            },
        }
    },
    "required": ["experiences"],
}


class IdentityReconciliationError(RuntimeError):
    pass


def reconcile_document_employment(document: Document, db: Session) -> dict[str, Any]:
    """Use the provider-neutral Intelligence Engine to semantically reconcile employment facts.

    The model proposes structured facts only. Database writes remain in this application service.
    Unconfirmed employment records sourced only from this document may be replaced; already
    reconciled facts are preserved and can only receive another supporting evidence link.
    """
    text = (document.source_metadata or {}).get("extracted_text", "")
    if not isinstance(text, str) or not text.strip():
        raise IdentityReconciliationError("No extracted document text is available")

    deterministic = CVParser().parse(text, str(document.id), document.document_category)
    task = (
        "Reconcile employment history from this professional document. Identify the real employer/organization, "
        "optional client, actual job title/designation, dates, responsibilities, achievements, technologies and "
        "industries. Do not mistake competency headings, skills, projects, section titles, or descriptive phrases "
        "for job titles or employers. Preserve the document's explicit wording when possible. If the document has "
        "multiple roles at the same employer, return separate roles. If an entry is ambiguous, keep the best-supported "
        "interpretation and lower confidence rather than inventing missing facts. Return JSON only matching the schema."
    )
    context = {
        "document": {
            "id": str(document.id),
            "filename": document.original_filename,
            "category": document.document_category,
            "subcategory": document.document_subcategory,
            "text": text[:50000],
        },
        "deterministic_candidate": {
            "professional": deterministic.get("professional", []),
            "confidence": deterministic.get("confidence"),
        },
    }
    request = IntelligenceRequest(
        task=task,
        context=context,
        output_schema=EMPLOYMENT_SCHEMA,
        tools=["document_lookup", "career_vault_search", "evidence_search"],
        temperature=0.0,
    )
    result = _run_engine(request)
    if result.status != "completed":
        detail = result.result if isinstance(result.result, dict) else {"error": str(result.result)}
        raise IdentityReconciliationError(f"AI reconciliation failed: {detail}")

    model_payload = _parse_model_result(result.result)
    experiences = [_sanitize_experience(x) for x in model_payload.get("experiences", []) if isinstance(x, dict)]
    experiences = [x for x in experiences if x["organization"] and x["title"]]

    applied, needs_review, protected = _apply_experiences(document, experiences, db)
    metadata = dict(document.source_metadata or {})
    metadata["ai_reconciliation"] = {
        "status": "completed",
        "engine_version": result.engine_version,
        "provider": result.provider,
        "model": result.model,
        "trace_id": str(result.trace_id) if result.trace_id else None,
        "applied_count": len(applied),
        "needs_review_count": len(needs_review),
        "protected_count": len(protected),
        "experiences": experiences,
    }
    document.source_metadata = metadata
    db.commit()
    return {
        "status": "completed" if not needs_review else "needs_review",
        "document_id": str(document.id),
        "model": result.model,
        "provider": result.provider,
        "trace_id": str(result.trace_id) if result.trace_id else None,
        "applied": applied,
        "needs_review": needs_review,
        "protected": protected,
        "experiences": experiences,
    }


def _run_engine(request: IntelligenceRequest):
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


def _parse_model_result(value: Any) -> dict[str, Any]:
    if not isinstance(value, str):
        return value if isinstance(value, dict) else {"experiences": []}
    cleaned = value.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise IdentityReconciliationError(f"AI reconciliation returned invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict) or not isinstance(parsed.get("experiences"), list):
        raise IdentityReconciliationError("AI reconciliation returned an invalid employment payload")
    return parsed


def _sanitize_experience(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "organization": str(value.get("organization") or "").strip()[:255],
        "client": _optional_text(value.get("client"), 255),
        "title": str(value.get("title") or "").strip()[:255],
        "start_date": _normalize_date(value.get("start_date")),
        "end_date": _normalize_date(value.get("end_date")),
        "is_current": bool(value.get("is_current")),
        "responsibilities": _string_list(value.get("responsibilities"), 20, 1000),
        "achievements": _string_list(value.get("achievements"), 20, 1000),
        "technologies": _string_list(value.get("technologies"), 40, 120),
        "industries": _string_list(value.get("industries"), 10, 120),
        "confidence": _bounded_float(value.get("confidence"), 0.0),
        "evidence_excerpt": _optional_text(value.get("evidence_excerpt"), 1000),
    }


def _apply_experiences(document: Document, experiences: list[dict[str, Any]], db: Session) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    candidate_id = document.candidate_id
    removable = (
        db.query(ProfessionalExperience)
        .filter(
            ProfessionalExperience.candidate_id == candidate_id,
            ProfessionalExperience.source_id == document.id,
            ProfessionalExperience.is_reconciled.is_(False),
            ProfessionalExperience.reconciliation_status == "extracted",
        )
        .all()
    )
    for item in removable:
        db.query(CareerFactEvidence).filter(
            CareerFactEvidence.candidate_id == candidate_id,
            CareerFactEvidence.document_id == document.id,
            CareerFactEvidence.fact_type == "employment",
            CareerFactEvidence.fact_id == item.id,
        ).delete(synchronize_session=False)
        db.delete(item)
    db.flush()

    applied: list[dict[str, Any]] = []
    needs_review: list[dict[str, Any]] = []
    protected: list[dict[str, Any]] = []
    for exp in experiences:
        confidence = exp["confidence"]
        verified = _find_verified_match(exp, candidate_id, db)
        if verified is not None:
            _ensure_evidence(document, verified, confidence, exp["evidence_excerpt"], db)
            protected.append({"experience_id": str(verified.id), "organization": verified.company, "title": verified.title, "confidence": confidence})
            continue

        target = _find_mutable_experience(exp, candidate_id, db)
        if target is None:
            target = ProfessionalExperience(candidate_id=candidate_id)
            db.add(target)

        target.company = exp["organization"]
        target.title = exp["title"]
        target.start_date = _date(exp["start_date"])
        target.end_date = _date(exp["end_date"])
        target.is_current = exp["is_current"]
        target.responsibilities = exp["responsibilities"]
        target.achievements = exp["achievements"]
        target.source_type = "document"
        target.source_id = document.id
        target.is_reconciled = confidence >= 0.85
        target.reconciliation_status = "ai_reconciled" if confidence >= 0.85 else "ai_review"
        db.flush()

        _ensure_evidence(document, target, confidence, exp["evidence_excerpt"], db)
        item = {"experience_id": str(target.id), "organization": target.company, "title": target.title, "confidence": confidence}
        (applied if confidence >= 0.85 else needs_review).append(item)

    return applied, needs_review, protected


def _find_verified_match(exp: dict[str, Any], candidate_id: UUID, db: Session) -> ProfessionalExperience | None:
    rows = db.query(ProfessionalExperience).filter(
        ProfessionalExperience.candidate_id == candidate_id,
        ProfessionalExperience.is_reconciled.is_(True),
    ).all()
    return _best_match(exp, rows, minimum=0.80)


def _find_mutable_experience(exp: dict[str, Any], candidate_id: UUID, db: Session) -> ProfessionalExperience | None:
    rows = db.query(ProfessionalExperience).filter(
        ProfessionalExperience.candidate_id == candidate_id,
        ProfessionalExperience.is_reconciled.is_(False),
    ).all()
    return _best_match(exp, rows, minimum=0.75)


def _best_match(exp: dict[str, Any], rows: list[ProfessionalExperience], minimum: float) -> ProfessionalExperience | None:
    best: tuple[float, ProfessionalExperience | None] = (0.0, None)
    for row in rows:
        score = 0.0
        if _norm(row.company) == _norm(exp["organization"]): score += 0.55
        if _norm(row.title) == _norm(exp["title"]): score += 0.30
        if exp["start_date"] and row.start_date and exp["start_date"][:7] == row.start_date.strftime("%Y-%m"): score += 0.10
        if exp["end_date"] and row.end_date and exp["end_date"][:7] == row.end_date.strftime("%Y-%m"): score += 0.05
        if score > best[0]: best = (score, row)
    return best[1] if best[0] >= minimum else None


def _ensure_evidence(document: Document, experience: ProfessionalExperience, confidence: float, excerpt: str | None, db: Session) -> None:
    evidence = db.query(CareerFactEvidence).filter(
        CareerFactEvidence.candidate_id == document.candidate_id,
        CareerFactEvidence.document_id == document.id,
        CareerFactEvidence.fact_type == "employment",
        CareerFactEvidence.fact_id == experience.id,
    ).first()
    value = excerpt or _fallback_excerpt({"organization": experience.company, "title": experience.title}, document)
    if evidence:
        evidence.confidence = confidence
        evidence.excerpt = value[:1000] if value else None
    else:
        db.add(CareerFactEvidence(
            candidate_id=document.candidate_id,
            document_id=document.id,
            fact_type="employment",
            fact_id=experience.id,
            relationship="supports",
            confidence=confidence,
            excerpt=value[:1000] if value else None,
        ))


def _fallback_excerpt(exp: dict[str, Any], document: Document) -> str | None:
    text = (document.source_metadata or {}).get("extracted_text", "")
    if not isinstance(text, str): return None
    org, title = exp["organization"], exp["title"]
    for line in text.splitlines():
        clean = line.strip()
        if org.lower() in clean.lower() and title.lower() in clean.lower(): return clean
    return f"{title} | {org}"


def _string_list(value: Any, limit: int, item_limit: int) -> list[str]:
    if not isinstance(value, list): return []
    seen: set[str] = set(); result: list[str] = []
    for item in value:
        text = str(item or "").strip(); key = _norm(text)
        if text and key and key not in seen:
            seen.add(key); result.append(text[:item_limit])
        if len(result) >= limit: break
    return result


def _optional_text(value: Any, limit: int) -> str | None:
    text = str(value or "").strip(); return text[:limit] if text else None


def _bounded_float(value: Any, default: float) -> float:
    try: number = float(value)
    except (TypeError, ValueError): return default
    return max(0.0, min(1.0, number))


def _normalize_date(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text: return None
    if re.fullmatch(r"\d{4}", text): return f"{text}-01-01"
    for fmt in ("%Y-%m-%d", "%Y-%m", "%b %Y", "%B %Y"):
        try: return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError: pass
    return None


def _date(value: str | None) -> datetime | None:
    if not value: return None
    try: return datetime.strptime(value[:10], "%Y-%m-%d")
    except ValueError: return None


def _norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()
