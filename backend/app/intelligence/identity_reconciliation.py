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
            "type": "array", "maxItems": 30,
            "items": {
                "type": "object", "additionalProperties": False,
                "properties": {
                    "organization": {"type": "string"}, "client": {"type": ["string", "null"]}, "title": {"type": "string"},
                    "start_date": {"type": ["string", "null"]}, "end_date": {"type": ["string", "null"]}, "is_current": {"type": "boolean"},
                    "responsibilities": {"type": "array", "items": {"type": "string"}, "maxItems": 20},
                    "achievements": {"type": "array", "items": {"type": "string"}, "maxItems": 20},
                    "technologies": {"type": "array", "items": {"type": "string"}, "maxItems": 40},
                    "industries": {"type": "array", "items": {"type": "string"}, "maxItems": 10},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}, "evidence_excerpt": {"type": ["string", "null"]},
                },
                "required": ["organization", "client", "title", "start_date", "end_date", "is_current", "responsibilities", "achievements", "technologies", "industries", "confidence", "evidence_excerpt"],
            },
        }
    },
    "required": ["experiences"],
}

MONTH_RE = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
DATE_RANGE_RE = re.compile(rf"\b({MONTH_RE})\s+(\d{{4}})\s*[-–—]\s*(?:(Present)|({MONTH_RE})\s+(\d{{4}}))\b", re.I)
YEAR_RANGE_RE = re.compile(r"\b((?:19|20)\d{2})\s*[-–—]\s*(?:(Present)|((?:19|20)\d{2}))\b", re.I)
EMPLOYMENT_HEADER_RE = re.compile(r"^(.{2,120}?)\s*\|\s*(.{2,160})$")


class IdentityReconciliationError(RuntimeError):
    pass


def reconcile_document_employment(document: Document, db: Session) -> dict[str, Any]:
    """Reconcile employment using AI enrichment constrained by source work-history anchors."""
    text = (document.source_metadata or {}).get("extracted_text", "")
    if not isinstance(text, str) or not text.strip():
        raise IdentityReconciliationError("No extracted document text is available")
    deterministic = CVParser().parse(text, str(document.id), document.document_category)
    anchors = _extract_source_employment_anchors(text)
    if not anchors:
        raise IdentityReconciliationError("No structured employment history could be safely identified in the source document")
    request = IntelligenceRequest(
        task="Reconcile employment history. source_employment_anchors are authoritative structural evidence. Preserve every anchor's organization, title, dates and client. Use AI only to enrich responsibilities, achievements, technologies and industries. Never create jobs from skills, competencies, projects, summary or headings. Multiple roles at one employer remain separate. Do not invent facts.",
        context={"document": {"id": str(document.id), "filename": document.original_filename, "category": document.document_category, "subcategory": document.document_subcategory, "text": text[:50000]}, "source_employment_anchors": anchors, "deterministic_candidate": {"professional": deterministic.get("professional", []), "confidence": deterministic.get("confidence")}},
        output_schema=EMPLOYMENT_SCHEMA, tools=["document_lookup", "career_vault_search", "evidence_search"], temperature=0.0,
    )
    result = _run_engine(request)
    if result.status != "completed":
        detail = result.result if isinstance(result.result, dict) else {"error": str(result.result)}
        raise IdentityReconciliationError(f"AI reconciliation failed: {detail}")
    model_payload = _parse_model_result(result.result)
    model_experiences = [_sanitize_experience(x) for x in model_payload.get("experiences", []) if isinstance(x, dict)]
    experiences = _merge_ai_with_source_anchors(model_experiences, anchors)
    applied, needs_review, protected, mutation_count = _apply_experiences(document, experiences, db)
    metadata = dict(document.source_metadata or {})
    metadata["ai_reconciliation"] = {"status": "completed", "engine_version": result.engine_version, "provider": result.provider, "model": result.model, "trace_id": str(result.trace_id) if result.trace_id else None, "applied_count": len(applied), "needs_review_count": len(needs_review), "protected_count": len(protected), "source_anchor_count": len(anchors), "model_experience_count": len(model_experiences), "mutation_count": mutation_count, "experiences": experiences}
    document.source_metadata = metadata
    db.commit()
    return {"status": "completed" if not needs_review else "needs_review", "document_id": str(document.id), "model": result.model, "provider": result.provider, "trace_id": str(result.trace_id) if result.trace_id else None, "applied": applied, "needs_review": needs_review, "protected": protected, "experiences": experiences, "source_anchor_count": len(anchors), "model_experience_count": len(model_experiences), "mutation_count": mutation_count}


def _extract_source_employment_anchors(text: str) -> list[dict[str, Any]]:
    """Extract only structurally anchored employment records from the work-history section."""
    lines = [line.strip() for line in (text or "").splitlines()]
    start = next((i for i, line in enumerate(lines) if _is_heading(line, "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE", "EMPLOYMENT HISTORY", "WORK HISTORY")), None)
    if start is None:
        return []
    stop_headings = {"EDUCATION", "CERTIFICATIONS", "CERTIFICATIONS & CREDENTIALS", "TECHNICAL EXPERTISE", "SKILLS", "SKILLS & CERTIFICATIONS OVERVIEW", "KEY PROJECTS & HARDWARE", "PERSONAL DETAILS", "ACHIEVEMENTS", "PUBLICATIONS", "LANGUAGES"}
    body: list[str] = []
    for line in lines[start + 1:]:
        if _is_heading(line, *stop_headings): break
        body.append(line)
    anchors: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in body:
        if not line: continue
        date_match = DATE_RANGE_RE.search(line) or YEAR_RANGE_RE.search(line)
        header = _employment_header(line)
        if header and date_match is None:
            if current: anchors.append(current)
            title, organization, client = header
            current = {"organization": organization, "client": client, "title": title, "start_date": None, "end_date": None, "is_current": False, "responsibilities": [], "achievements": [], "technologies": [], "industries": [], "confidence": 0.97, "evidence_excerpt": line}
            continue
        if current is None:
            compact = re.match(r"^(.{3,120}?)\s*[-–—]\s*(.{2,120}?)\s*\(((?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2}|Present)\)$", line, re.I)
            if compact:
                title, organization, start_year, end_year = compact.groups()
                anchors.append({"organization": organization.strip(), "client": None, "title": title.strip(), "start_date": f"{start_year}-01-01", "end_date": None if end_year.lower() == "present" else f"{end_year}-12-31", "is_current": end_year.lower() == "present", "responsibilities": [], "achievements": [], "technologies": [], "industries": [], "confidence": 0.94, "evidence_excerpt": line})
            continue
        if date_match:
            current["start_date"], current["end_date"], current["is_current"] = _parse_range_match(date_match)
            continue
        clean = re.sub(r"^[•*✓▶-]+\s*", "", line).strip()
        if clean and clean.lower() != "earlier roles": current["responsibilities"].append(clean[:1000])
    if current: anchors.append(current)
    return anchors


def _employment_header(line: str) -> tuple[str, str, str | None] | None:
    match = EMPLOYMENT_HEADER_RE.match(line)
    if not match: return None
    left, right = match.group(1).strip(), match.group(2).strip()
    if not _looks_like_title(left): return None
    client_match = re.search(r"\(\s*client\s*:\s*([^\)]+)\)", right, re.I)
    client = client_match.group(1).strip() if client_match else None
    organization = re.sub(r"\s*\(\s*client\s*:\s*[^\)]+\)\s*", "", right, flags=re.I).strip(" ,")
    if not organization or not _looks_like_organization(organization): return None
    return left, organization, client


def _looks_like_title(value: str) -> bool:
    return bool(re.search(r"\b(architect|engineer|manager|director|lead|consultant|analyst|specialist|executive|administrator|officer|developer|head|principal|technical)\b", value, re.I))


def _looks_like_organization(value: str) -> bool:
    if len(value) < 2 or len(value) > 160: return False
    return not re.search(r"\b(strategic leadership|stakeholder management|core competencies|technical expertise|networking|cybersecurity|solution architecture|leadership & strategy)\b", value, re.I)


def _is_heading(line: str, *headings: str) -> bool:
    normalized = re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9&+ ]", " ", (line or "").upper())).strip()
    return normalized in {re.sub(r"[^A-Z0-9&+ ]", " ", heading.upper()).strip() for heading in headings}


def _parse_range_match(match: re.Match) -> tuple[str | None, str | None, bool]:
    groups = match.groups()
    if len(groups) == 5:
        start_month, start_year, present, end_month, end_year = groups
        start_date = f"{start_year}-{_month_number(start_month):02d}-01"
        return (start_date, None, True) if present else (start_date, f"{end_year}-{_month_number(end_month):02d}-01", False)
    start_year, present, end_year = groups
    return (f"{start_year}-01-01", None, True) if present else (f"{start_year}-01-01", f"{end_year}-12-31", False)


def _month_number(value: str) -> int:
    return {"jan":1,"january":1,"feb":2,"february":2,"mar":3,"march":3,"apr":4,"april":4,"may":5,"jun":6,"june":6,"jul":7,"july":7,"aug":8,"august":8,"sep":9,"sept":9,"september":9,"oct":10,"october":10,"nov":11,"november":11,"dec":12,"december":12}[value.lower()]


def _merge_ai_with_source_anchors(model_experiences: list[dict[str, Any]], anchors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    used: set[int] = set()
    for anchor in anchors:
        best_index = None; best_score = 0.0
        for index, candidate in enumerate(model_experiences):
            if index in used: continue
            score = _identity_score(anchor, candidate)
            if score > best_score: best_score, best_index = score, index
        merged = dict(anchor)
        if best_index is not None and best_score >= 0.45:
            used.add(best_index); candidate = model_experiences[best_index]
            for field in ("responsibilities", "achievements", "technologies", "industries"):
                if candidate.get(field): merged[field] = candidate[field]
            merged["confidence"] = max(float(anchor.get("confidence", 0.97)), float(candidate.get("confidence", 0.0)))
            if candidate.get("evidence_excerpt"): merged["evidence_excerpt"] = candidate["evidence_excerpt"]
        result.append(merged)
    return result


def _identity_score(left: dict[str, Any], right: dict[str, Any]) -> float:
    return _token_overlap(left.get("organization"), right.get("organization")) * 0.55 + _token_overlap(left.get("title"), right.get("title")) * 0.35 + (_token_overlap(left.get("client"), right.get("client")) * 0.10 if left.get("client") and right.get("client") else 0.0)


def _token_overlap(left: Any, right: Any) -> float:
    a, b = set(_norm(left).split()), set(_norm(right).split())
    return len(a & b) / len(a | b) if a and b else 0.0


def _apply_experiences(document: Document, experiences: list[dict[str, Any]], db: Session) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], int]:
    """Safely reconcile employment without deleting or overwriting user-confirmed records."""
    candidate_id = document.candidate_id
    incoming = [x for x in experiences if isinstance(x, dict)]
    source_text = (document.source_metadata or {}).get("extracted_text", "")
    anchors = _extract_source_employment_anchors(source_text) if isinstance(source_text, str) else []
    if anchors:
        incoming = _merge_ai_with_source_anchors(incoming, anchors)
    if not incoming:
        return [], [], [], 0

    applied: list[dict[str, Any]] = []
    needs_review: list[dict[str, Any]] = []
    protected: list[dict[str, Any]] = []
    mutation_count = 0

    # Protection check MUST happen before loading the mutable working set.
    # A verified/user-confirmed match is never passed into mutable reconciliation.
    for exp in incoming:
        confidence = _bounded_float(exp.get("confidence"), 0.0)
        verified = _find_verified_match(exp, candidate_id, db)
        if verified:
            _ensure_evidence(document, verified, confidence, exp.get("evidence_excerpt"), db)
            protected.append({"experience_id": str(verified.id), "organization": verified.company, "title": verified.title, "confidence": confidence})
            continue

        # Load only mutable records for the upsert path. Confirmed rows are excluded
        # at the query result boundary as a second protection layer.
        existing = db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == candidate_id).all()
        mutable_existing = [row for row in existing if not (row.is_reconciled and row.reconciliation_status == "user_confirmed")]

        target = _best_match(exp, mutable_existing, minimum=0.75)
        if target is None:
            target = ProfessionalExperience(candidate_id=candidate_id)
            db.add(target)
            mutable_existing.append(target)
            mutation_count += 1
        before = (target.company, target.client, target.title, target.start_date, target.end_date, target.is_current, target.responsibilities, target.achievements, target.technologies, target.industries)
        target.company = exp["organization"]
        target.client = exp["client"]
        target.title = exp["title"]
        target.start_date = _date(exp["start_date"])
        target.end_date = _date(exp["end_date"])
        target.is_current = exp["is_current"]
        target.responsibilities = exp["responsibilities"]
        target.achievements = exp["achievements"]
        target.technologies = exp["technologies"]
        target.industries = exp["industries"]
        target.industry = exp["industries"][0] if exp["industries"] else target.industry
        target.source_type = "document"
        target.source_id = document.id
        target.is_reconciled = confidence >= 0.85
        target.reconciliation_status = "ai_reconciled" if confidence >= 0.85 else "ai_review"
        db.flush()
        after = (target.company, target.client, target.title, target.start_date, target.end_date, target.is_current, target.responsibilities, target.achievements, target.technologies, target.industries)
        if before != after: mutation_count += 1
        _ensure_evidence(document, target, confidence, exp.get("evidence_excerpt"), db)
        item = {"experience_id": str(target.id), "organization": target.company, "client": target.client, "title": target.title, "confidence": confidence}
        (applied if confidence >= 0.85 else needs_review).append(item)
    return applied, needs_review, protected, mutation_count


def _find_verified_match(exp: dict[str, Any], candidate_id: UUID, db: Session) -> ProfessionalExperience | None:
    rows = db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == candidate_id, ProfessionalExperience.is_reconciled.is_(True), ProfessionalExperience.reconciliation_status == "user_confirmed").all()
    return _best_match(exp, rows, minimum=0.80)


def _best_match(exp: dict[str, Any], rows: list[ProfessionalExperience], minimum: float) -> ProfessionalExperience | None:
    best: tuple[float, ProfessionalExperience | None] = (0.0, None)
    for row in rows:
        score = 0.0
        if _norm(row.company) == _norm(exp["organization"]): score += 0.55
        if _norm(row.title) == _norm(exp["title"]): score += 0.30
        if exp["client"] and _norm(row.client) == _norm(exp["client"]): score += 0.10
        if exp["start_date"] and row.start_date and exp["start_date"][:7] == row.start_date.strftime("%Y-%m"): score += 0.10
        if exp["end_date"] and row.end_date and exp["end_date"][:7] == row.end_date.strftime("%Y-%m"): score += 0.05
        if score > best[0]: best = (score, row)
    return best[1] if best[0] >= minimum else None


def _ensure_evidence(document: Document, experience: ProfessionalExperience, confidence: float, excerpt: str | None, db: Session) -> None:
    evidence = db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id == document.candidate_id, CareerFactEvidence.document_id == document.id, CareerFactEvidence.fact_type == "employment", CareerFactEvidence.fact_id == experience.id).first()
    value = excerpt or _fallback_excerpt({"organization": experience.company, "title": experience.title}, document)
    if evidence:
        evidence.confidence = confidence; evidence.excerpt = value[:1000] if value else None
    else:
        db.add(CareerFactEvidence(candidate_id=document.candidate_id, document_id=document.id, fact_type="employment", fact_id=experience.id, relationship="supports", confidence=confidence, excerpt=value[:1000] if value else None))


def _fallback_excerpt(exp: dict[str, Any], document: Document) -> str | None:
    text = (document.source_metadata or {}).get("extracted_text", "")
    if not isinstance(text, str): return None
    org, title = exp["organization"], exp["title"]
    for line in text.splitlines():
        clean = line.strip()
        if org.lower() in clean.lower() and title.lower() in clean.lower(): return clean
    return f"{title} | {org}"


def _sanitize_experience(item: dict[str, Any]) -> dict[str, Any]:
    return {"organization": str(item.get("organization") or "").strip(), "client": str(item.get("client")).strip() if item.get("client") else None, "title": str(item.get("title") or "").strip(), "start_date": _normalize_date(item.get("start_date")), "end_date": _normalize_date(item.get("end_date")), "is_current": bool(item.get("is_current")), "responsibilities": _string_list(item.get("responsibilities"), 20, 1000), "achievements": _string_list(item.get("achievements"), 20, 1000), "technologies": _string_list(item.get("technologies"), 40, 200), "industries": _string_list(item.get("industries"), 10, 100), "confidence": _bounded_float(item.get("confidence"), 0.0), "evidence_excerpt": _optional_text(item.get("evidence_excerpt"), 1000)}


def _string_list(value: Any, limit: int, item_limit: int) -> list[str]:
    if not isinstance(value, list): return []
    seen: set[str] = set(); result: list[str] = []
    for item in value:
        text = str(item or "").strip(); key = _norm(text)
        if text and key and key not in seen: seen.add(key); result.append(text[:item_limit])
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


def _run_engine(request: IntelligenceRequest):
    try: return asyncio.run(engine.execute(request))
    except RuntimeError as exc:
        if "asyncio.run() cannot be called" not in str(exc): raise
        loop = asyncio.new_event_loop()
        try: return loop.run_until_complete(engine.execute(request))
        finally: loop.close()


def _parse_model_result(value: Any) -> dict[str, Any]:
    if isinstance(value, dict): return value
    if not isinstance(value, str): raise IdentityReconciliationError("AI returned an invalid employment reconciliation payload")
    text = re.sub(r"^```(?:json)?\s*", "", value.strip(), flags=re.I); text = re.sub(r"\s*```$", "", text)
    try: parsed = json.loads(text)
    except json.JSONDecodeError as exc: raise IdentityReconciliationError(f"AI returned invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict): raise IdentityReconciliationError("AI employment reconciliation result must be a JSON object")
    return parsed
