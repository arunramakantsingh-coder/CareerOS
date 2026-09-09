from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.career_fact_evidence import CareerFactEvidence
from app.models.document import Document
from app.models.persona import Persona
from app.models.professional_experience import ProfessionalExperience
from app.intelligence.knowledge_context import EvidenceReference, KnowledgeItem, normalize_trust_state


def build_professional_identity_context(
    db: Session,
    candidate_id: UUID,
    include_documents: bool = True,
) -> dict[str, Any]:
    """Create a bounded, provenance-aware read model for Intelligence Engine prompts."""
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == candidate_id).first()
    if not profile:
        return {"profile": None, "facts": [], "documents": [], "personas": []}

    facts: list[dict[str, Any]] = []
    for item in _profile_facts(profile):
        facts.append(item.to_dict())

    for experience in db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == candidate_id).all():
        facts.append(_experience_item(experience, db).to_dict())

    for skill in db.query(CandidateSkill).filter(CandidateSkill.candidate_id == candidate_id).all():
        facts.append(_skill_item(skill, db).to_dict())

    for cert in db.query(CandidateCertification).filter(CandidateCertification.candidate_id == candidate_id).all():
        facts.append(_cert_item(cert, db).to_dict())

    for education in db.query(CandidateEducation).filter(CandidateEducation.candidate_id == candidate_id).all():
        facts.append(_education_item(education, db).to_dict())

    context: dict[str, Any] = {
        "profile": {
            "id": str(profile.id),
            "full_name": profile.full_name,
            "primary_email": profile.primary_email,
            "location": profile.location,
            "title": profile.title,
            "summary": profile.summary,
            "linkedin_url": profile.linkedin_url,
            "completeness_score": profile.completeness_score,
            "reconciliation_status": profile.reconciliation_status,
        },
        "facts": facts,
        "personas": [],
    }

    # Persona is keyed to the application user in the current model rather than
    # directly to CandidateProfile. Keep this lookup user-scoped and do not invent
    # a candidate_id relationship that does not exist in the schema.
    personas = db.query(Persona).filter(Persona.user_id == profile.user_id).all()
    context["personas"] = [
        {
            "id": str(persona.id),
            "name": getattr(persona, "name", None),
            "description": getattr(persona, "description", None),
            "status": getattr(persona, "status", None),
        }
        for persona in personas
    ]

    if include_documents:
        context["documents"] = [
            {
                "id": str(document.id),
                "filename": document.original_filename,
                "category": document.document_category,
                "subcategory": document.document_subcategory,
                "detected_type": document.detected_type,
                "verification_status": document.verification_status,
                "processing_stage": document.processing_stage,
                "representation": (document.source_metadata or {}).get("career_os_representation"),
            }
            for document in db.query(Document).filter(Document.candidate_id == candidate_id).all()
        ]
    else:
        context["documents"] = []

    return context


def _profile_facts(profile: CandidateProfile) -> list[KnowledgeItem]:
    values = {
        "full_name": profile.full_name,
        "primary_email": profile.primary_email,
        "primary_phone": profile.primary_phone,
        "location": profile.location,
        "title": profile.title,
        "summary": profile.summary,
        "linkedin_url": profile.linkedin_url,
    }
    # CandidateProfile currently has no field-level provenance/confirmation flags.
    # Do not claim these values are user-confirmed; keep the baseline conservative.
    return [
        KnowledgeItem("profile", key, value, trust_state="EXTRACTED")
        for key, value in values.items()
        if value
    ]


def _evidence(candidate_id: UUID, fact_type: str, fact_id: UUID, db: Session) -> tuple[EvidenceReference, ...]:
    links = db.query(CareerFactEvidence).filter(
        CareerFactEvidence.candidate_id == candidate_id,
        CareerFactEvidence.fact_type == fact_type,
        CareerFactEvidence.fact_id == fact_id,
    ).all()
    result: list[EvidenceReference] = []
    for link in links:
        result.append(EvidenceReference(
            document_id=str(link.document_id),
            fact_type=link.fact_type,
            fact_id=str(link.fact_id),
            excerpt=link.excerpt,
            confidence=link.confidence,
            trust_state="EXTRACTED",
            source_type="document",
        ))
    return tuple(result)


def _experience_item(item: ProfessionalExperience, db: Session) -> KnowledgeItem:
    value = {
        "company": item.company,
        "title": item.title,
        "start_date": item.start_date.isoformat() if item.start_date else None,
        "end_date": item.end_date.isoformat() if item.end_date else None,
        "is_current": item.is_current,
        "responsibilities": item.responsibilities or [],
        "achievements": item.achievements or [],
        "industry": item.industry,
    }
    state = normalize_trust_state("USER-CONFIRMED" if item.is_reconciled else "EXTRACTED")
    return KnowledgeItem("employment", str(item.id), value, _evidence(item.candidate_id, "employment", item.id, db), state)


def _skill_item(item: CandidateSkill, db: Session) -> KnowledgeItem:
    value = {"name": item.name, "category": item.category, "confidence": item.confidence}
    state = normalize_trust_state("USER-CONFIRMED" if getattr(item, "is_verified", False) else "EXTRACTED")
    return KnowledgeItem("skill", str(item.id), value, _evidence(item.candidate_id, "skill", item.id, db), state)


def _cert_item(item: CandidateCertification, db: Session) -> KnowledgeItem:
    value = {
        "name": item.name,
        "issuer": item.issuer,
        "issue_date": item.issue_date.isoformat() if item.issue_date else None,
        "expiry_date": item.expiry_date.isoformat() if item.expiry_date else None,
        "credential_reference": item.credential_reference,
        "confidence": item.confidence,
    }
    return KnowledgeItem("certification", str(item.id), value, _evidence(item.candidate_id, "certification", item.id, db), "EXTRACTED")


def _education_item(item: CandidateEducation, db: Session) -> KnowledgeItem:
    value = {
        "institution": item.institution,
        "degree": item.degree,
        "field_of_study": item.field_of_study,
        "start_date": item.start_date.isoformat() if item.start_date else None,
        "end_date": item.end_date.isoformat() if item.end_date else None,
        "confidence": item.confidence,
    }
    return KnowledgeItem("education", str(item.id), value, _evidence(item.candidate_id, "education", item.id, db), "EXTRACTED")
