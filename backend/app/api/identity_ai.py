from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.intelligence.ai_cv_ingestion import AICVIngestionError, ingest_cv_with_ai
from app.intelligence.document_enrichment import DocumentEnrichmentError, enrich_document
from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.career_fact_evidence import CareerFactEvidence
from app.models.document import Document
from app.models.persona import Persona
from app.models.persona_suggestion import PersonaSuggestion
from app.models.professional_experience import ProfessionalExperience
from app.models.user import User

router = APIRouter(prefix="/identity", tags=["professional-identity-ai"])


def _profile(user: User, db: Session) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id, CandidateProfile.is_active.is_(True)).first()
    if not profile:
        raise HTTPException(404, "Professional profile not found")
    return profile


def _links(profile_id: UUID, fact_type: str, fact_id: str, db: Session) -> list[dict]:
    rows = db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id == profile_id, CareerFactEvidence.fact_type == fact_type, CareerFactEvidence.fact_id == UUID(str(fact_id))).all()
    if not rows: return []
    docs = {d.id: d for d in db.query(Document).filter(Document.id.in_([x.document_id for x in rows])).all()}
    return [{"document_id": str(x.document_id), "display_name": docs[x.document_id].user_label or docs[x.document_id].filename if x.document_id in docs else "Document", "category": docs[x.document_id].document_category if x.document_id in docs else None, "confidence": x.confidence, "relationship": x.relationship, "excerpt": x.excerpt} for x in rows]


def _fact(item, fact_type: str, profile_id: UUID, db: Session) -> dict:
    result = {"id": str(item.id), **{k: getattr(item, k) for k in item.__table__.columns.keys() if k not in {"id", "candidate_id"}}}
    result["evidence"] = _links(profile_id, fact_type, str(item.id), db)
    result["evidence_state"] = _evidence_state(result["evidence"])
    return result


def _evidence_state(links: list[dict]) -> str:
    if any(x.get("category") != "cv" for x in links): return "supported"
    if links: return "cv_source"
    return "no_evidence_uploaded"


def _json_fact(item: dict, fact_type: str, profile_id: UUID, db: Session) -> dict:
    result = dict(item)
    result["evidence"] = _links(profile_id, fact_type, str(item.get("id")), db) if item.get("id") else []
    result["evidence_state"] = _evidence_state(result["evidence"])
    return result


def _section_score(items: list[dict], require_dedicated: bool = True) -> tuple[float, int]:
    if not items: return 0.0, 0
    if not require_dedicated: return 100.0, 0
    supported = sum(1 for x in items if x["evidence_state"] == "supported")
    return round(supported / len(items) * 100, 1), len(items) - supported


def _calculate(profile, experiences, educations, certifications, skills, projects, accomplishments, documents, work_preferences, db):
    # Content quality and evidence quality are deliberately separate. A CV-derived
    # fact is valid reported information, but a dedicated supporting document is stronger evidence.
    profile_content = sum(bool(getattr(profile, f, None)) for f in ("full_name", "location", "title", "primary_email", "primary_phone", "linkedin_url")) / 6
    summary_content = 1 if profile.summary else 0
    emp = [_fact(x, "employment", profile.id, db) for x in experiences]
    edu = [_fact(x, "education", profile.id, db) for x in educations]
    cert = [_fact(x, "certification", profile.id, db) for x in certifications]
    skill = [_fact(x, "skill", profile.id, db) for x in skills]
    proj = [_json_fact(x, "project", profile.id, db) for x in projects]
    acc = [_json_fact(x, "accomplishment", profile.id, db) for x in accomplishments]
    scores = {
        "personal": round(profile_content * 100, 1),
        "summary": round(summary_content * 100, 1),
        "employment": _section_score(emp)[0],
        "education": _section_score(edu)[0],
        "certifications": _section_score(cert)[0],
        "skills": 100.0 if skill else 0.0,
        "projects": _section_score(proj)[0],
        "accomplishments": _section_score(acc)[0],
        "career_profile": 100.0 if work_preferences else 0.0,
    }
    weights = {"personal": 10, "summary": 10, "employment": 20, "education": 10, "certifications": 10, "skills": 15, "projects": 10, "accomplishments": 5, "career_profile": 10}
    completeness = round(sum(weights[k] * scores[k] / 100 for k in weights), 1)
    evidence_requirements = []
    for kind, label, rows in (("employment", "Employment", emp), ("education", "Education", edu), ("certification", "Certification", cert), ("project", "Project", proj), ("accomplishment", "Accomplishment", acc)):
        for row in rows:
            if row["evidence_state"] != "supported":
                title = row.get("title") or row.get("degree") or row.get("name") or label
                evidence_requirements.append({"fact_type": kind, "fact_id": row["id"], "label": title, "status": "no_evidence_uploaded", "action": "upload_evidence"})
    evidence_total = sum(len(x) for x in (emp, edu, cert, proj, acc))
    evidence_supported = sum(1 for x in (emp, edu, cert, proj, acc) for row in x if row["evidence_state"] == "supported")
    evidence_coverage = round((evidence_supported / evidence_total * 100) if evidence_total else (100 if documents else 0), 1)
    return completeness, evidence_coverage, emp, edu, cert, skill, proj, acc, evidence_requirements, scores


@router.post("/documents/{document_id}/ai-reconcile")
def ai_reconcile_document(document_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """AI-first ingestion: understand the complete CV and populate CareerOS identity facts."""
    profile = _profile(user, db)
    document = db.query(Document).filter(Document.id == document_id, Document.candidate_id == profile.id).first()
    if not document: raise HTTPException(404, "Document not found")
    if document.document_category not in {"cv", "employment", "other"}: raise HTTPException(400, "AI CV ingestion is only available for CV or employment documents")
    try:
        result = ingest_cv_with_ai(document, profile, db)
        try: enrich_document(document, profile, db); db.commit()
        except DocumentEnrichmentError: pass
        return result
    except AICVIngestionError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/documents/{document_id}/ai-enrich")
def ai_enrich_document(document_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _profile(user, db)
    document = db.query(Document).filter(Document.id == document_id, Document.candidate_id == profile.id).first()
    if not document: raise HTTPException(404, "Document not found")
    try:
        result = enrich_document(document, profile, db); db.commit(); return {"status": "completed", "document_id": str(document.id), **result}
    except DocumentEnrichmentError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/overview-enriched")
def enriched_overview(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _profile(user, db)
    experiences = db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == profile.id).order_by(ProfessionalExperience.start_date.desc().nullslast()).all()
    educations = db.query(CandidateEducation).filter(CandidateEducation.candidate_id == profile.id).all()
    certifications = db.query(CandidateCertification).filter(CandidateCertification.candidate_id == profile.id).all()
    skills = db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id).all()
    documents = db.query(Document).filter(Document.candidate_id == profile.id).order_by(Document.created_at.desc()).all()
    projects = profile.projects or []
    accomplishments = profile.accomplishments or []
    completeness, evidence_coverage, emp, edu, cert, skill, proj, acc, evidence_requirements, scores = _calculate(profile, experiences, educations, certifications, skills, projects, accomplishments, documents, profile.work_preferences, db)
    profile.completeness_score = completeness
    profile.completeness_breakdown = scores
    db.commit()
    sections = {
        "personal": {"label": "Personal details & professional identity", "status": "complete" if scores["personal"] >= 100 else "needs_review"},
        "summary": {"label": "Profile summary", "status": "complete" if scores["summary"] >= 100 else "needs_input"},
        "employment": {"label": "Employment history", "status": "complete" if scores["employment"] >= 100 else "evidence_needed" if experiences else "needs_input"},
        "education": {"label": "Education", "status": "complete" if scores["education"] >= 100 else "evidence_needed" if educations else "needs_input"},
        "certifications": {"label": "Certifications & credentials", "status": "complete" if scores["certifications"] >= 100 else "evidence_needed" if certifications else "needs_input"},
        "skills": {"label": "Key skills & IT skills", "status": "complete" if scores["skills"] >= 100 else "needs_input"},
        "projects": {"label": "Projects", "status": "complete" if scores["projects"] >= 100 else "evidence_needed" if projects else "needs_input"},
        "accomplishments": {"label": "Accomplishments", "status": "complete" if scores["accomplishments"] >= 100 else "evidence_needed" if accomplishments else "needs_input"},
        "career_profile": {"label": "Career profile & preferences", "status": "complete" if scores["career_profile"] >= 100 else "needs_review"},
    }
    personas = db.query(Persona).filter(Persona.user_id == user.id).all()
    suggestions = db.query(PersonaSuggestion).filter(PersonaSuggestion.user_id == user.id, PersonaSuggestion.status == "suggested").order_by(PersonaSuggestion.confidence.desc()).all()
    return {
        "profile": {"id": str(profile.id), "full_name": profile.full_name, "location": profile.location, "title": profile.title, "summary": profile.summary, "primary_email": profile.primary_email, "primary_phone": profile.primary_phone, "linkedin_url": profile.linkedin_url, "years_experience": profile.years_experience, "industries": profile.industries or [], "seniority": profile.seniority, "work_preferences": profile.work_preferences or {}, "completeness_score": completeness},
        "experiences": emp, "educations": edu, "certifications": cert, "skills": skill, "projects": proj, "accomplishments": acc,
        "documents": [{"id": str(d.id), "display_name": d.user_label or d.filename, "category": d.document_category, "detected_type": d.detected_type, "linked_fact_count": db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id == profile.id, CareerFactEvidence.document_id == d.id).count()} for d in documents],
        "personas": [{"id": str(x.id), "name": x.name, "description": x.description, "positioning": x.positioning, "is_active": x.is_active, "target_titles": x.target_titles or []} for x in personas],
        "persona_suggestions": [{"id": str(x.id), "name": x.name, "role_family": x.role_family, "positioning": x.positioning, "target_titles": x.target_titles or [], "confidence": x.confidence, "reason": x.reason, "missing_evidence": x.missing_evidence or [], "supporting_document_ids": x.supporting_document_ids or []} for x in suggestions],
        "section_navigation": sections,
        "intelligence": {"profile_completeness": completeness, "evidence_coverage": evidence_coverage, "data_confidence": round(sum(float(x.confidence or 0) for x in certifications + educations + skills) / max(1, len(certifications) + len(educations) + len(skills)) * 100, 1), "persona_readiness": 100.0 if personas else min(100.0, round((len(experiences) * 15 + len(skills) * 2), 1))},
        "evidence_requirements": evidence_requirements,
    }
