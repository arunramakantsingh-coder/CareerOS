from __future__ import annotations

import asyncio
import json
import re
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.intelligence.contracts import IntelligenceRequest
from app.intelligence.engine import engine
from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.document import Document
from app.models.professional_experience import ProfessionalExperience


VALIDATION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "status": {"type": "string", "enum": ["passed", "needs_review"]},
        "summary": {"type": "string"},
        "issues": {
            "type": "array",
            "maxItems": 40,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "section": {"type": "string"},
                    "type": {"type": "string"},
                    "severity": {"type": "string", "enum": ["info", "warning", "critical"]},
                    "description": {"type": "string"},
                },
                "required": ["section", "type", "severity", "description"],
            },
        },
        "duplicate_candidates": {
            "type": "array",
            "maxItems": 30,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "section": {"type": "string"},
                    "items": {"type": "array", "items": {"type": "string"}, "maxItems": 10},
                    "reason": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["section", "items", "reason", "confidence"],
            },
        },
    },
    "required": ["status", "summary", "issues", "duplicate_candidates"],
}


class ProfileValidationError(RuntimeError):
    pass


def validate_reconciled_profile(document: Document, profile: CandidateProfile, db: Session) -> dict[str, Any]:
    """Run a post-persistence AI audit of the Professional Profile.

    The validator is advisory and never becomes the system of record. It receives the
    persisted profile plus the source CV, identifies duplication/cross-section issues,
    and writes only a bounded validation report into existing JSON metadata.
    """
    snapshot = _snapshot(profile, db)
    deterministic = _deterministic_checks(snapshot)
    request = IntelligenceRequest(
        task=(
            "Perform a post-reconciliation quality audit of the persisted CareerOS Professional Profile. "
            "The source CV is authoritative. Check whether populated sections are faithful to the CV, "
            "whether education/certifications/skills contain duplicates or cross-section contamination, "
            "whether employment roles remain separate, and whether obviously repeated facts should be reviewed. "
            "Do not invent missing facts. This is validation only; do not propose new career facts."
        ),
        task_type="profile_validation",
        context={
            "source_cv": {"filename": document.original_filename, "text": ((document.source_metadata or {}).get("extracted_text") or "")[:70000]},
            "persisted_profile": snapshot,
            "deterministic_checks": deterministic,
        },
        output_schema=VALIDATION_SCHEMA,
        tools=[],
        temperature=0.0,
    )
    result = _run(request)
    if result.status != "completed":
        return {
            "status": "needs_review",
            "summary": "Post-reconciliation AI validation could not be completed.",
            "issues": [{"section": "profile", "type": "validation_unavailable", "severity": "warning", "description": str(result.result)[:500]}],
            "duplicate_candidates": deterministic["duplicate_candidates"],
            "provider": result.provider,
            "model": result.model,
            "trace_id": str(result.trace_id) if result.trace_id else None,
        }
    report = _parse(result.result)
    if deterministic["duplicate_candidates"]:
        report.setdefault("duplicate_candidates", [])
        report["duplicate_candidates"] = deterministic["duplicate_candidates"] + [
            item for item in report["duplicate_candidates"] if item not in deterministic["duplicate_candidates"]
        ]
        if report.get("status") == "passed":
            report["status"] = "needs_review"
    report["provider"] = result.provider
    report["model"] = result.model
    report["trace_id"] = str(result.trace_id) if result.trace_id else None
    report["deterministic_checks"] = deterministic
    return report


def _snapshot(profile: CandidateProfile, db: Session) -> dict[str, Any]:
    experiences = db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == profile.id).all()
    skills = db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id).all()
    certifications = db.query(CandidateCertification).filter(CandidateCertification.candidate_id == profile.id).all()
    education = db.query(CandidateEducation).filter(CandidateEducation.candidate_id == profile.id).all()
    return {
        "profile": {"full_name": profile.full_name, "title": profile.title, "summary": profile.summary, "location": profile.location},
        "experiences": [{"id": str(x.id), "title": x.title, "company": x.company, "client": x.client, "start_date": x.start_date, "end_date": x.end_date} for x in experiences],
        "education": [{"id": str(x.id), "degree": x.degree, "institution": x.institution, "field_of_study": x.field_of_study} for x in education],
        "certifications": [{"id": str(x.id), "name": x.name, "issuer": x.issuer, "credential_reference": x.credential_reference} for x in certifications],
        "skills": [{"id": str(x.id), "name": x.name, "category": x.category} for x in skills],
        "projects": profile.projects or [],
        "accomplishments": profile.accomplishments or [],
    }


def _deterministic_checks(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "duplicate_candidates": _duplicate_candidates(snapshot),
        "empty_sections": [name for name in ("experiences", "education", "certifications", "skills") if not snapshot.get(name)],
    }


def _duplicate_candidates(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for section in ("education", "certifications", "skills"):
        rows = snapshot.get(section) or []
        for i, left in enumerate(rows):
            for right in rows[i + 1 :]:
                if section == "education":
                    same_degree = _norm(left.get("degree")) == _norm(right.get("degree"))
                    institutions = (_tokens(left.get("institution")), _tokens(right.get("institution")))
                    overlap = _overlap(*institutions)
                    duplicate = same_degree and (overlap >= 0.72 or _subset(*institutions))
                elif section == "certifications":
                    names = (_tokens(left.get("name")), _tokens(right.get("name")))
                    issuer_overlap = _overlap(_tokens(left.get("issuer")), _tokens(right.get("issuer")))
                    duplicate = (_norm(left.get("name")) == _norm(right.get("name"))) or (_subset(*names) and issuer_overlap >= 0.5)
                else:
                    duplicate = _norm(left.get("name")) == _norm(right.get("name"))
                if duplicate:
                    findings.append({"section": section, "items": [str(left.get("id")), str(right.get("id"))], "reason": "Records appear to represent the same fact after normalization.", "confidence": 0.95})
    return findings[:30]


def _tokens(value: Any) -> set[str]:
    return set(_norm(value).split())


def _subset(left: set[str], right: set[str]) -> bool:
    return bool(left and right and (left <= right or right <= left))


def _overlap(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def _parse(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        raise ProfileValidationError("AI validation returned an invalid payload")
    text = re.sub(r"^```(?:json)?\s*", "", value.strip(), flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProfileValidationError(f"AI validation returned invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ProfileValidationError("AI validation result must be a JSON object")
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
