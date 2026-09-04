from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.document import Document
from app.models.extraction_result import ExtractionResult
from app.models.external_identity import ExternalIdentity
from app.models.professional_experience import ProfessionalExperience
from app.models.user import User
from app.api.candidate import calculate_completeness

router = APIRouter(prefix="/profile/intelligence", tags=["profile-intelligence"])


def profile_for_user(current_user: User, db: Session) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True,
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("")
def get_profile_intelligence(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = profile_for_user(current_user, db)
    experiences = db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == profile.id).order_by(ProfessionalExperience.start_date.desc()).all()
    skills = db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id).order_by(CandidateSkill.name.asc()).all()
    certifications = db.query(CandidateCertification).filter(CandidateCertification.candidate_id == profile.id).order_by(CandidateCertification.issue_date.desc()).all()
    educations = db.query(CandidateEducation).filter(CandidateEducation.candidate_id == profile.id).order_by(CandidateEducation.end_date.desc()).all()
    documents = db.query(Document).filter(Document.candidate_id == profile.id).order_by(Document.created_at.desc()).all()
    extractions = db.query(ExtractionResult).filter(ExtractionResult.candidate_id == profile.id).order_by(ExtractionResult.created_at.desc()).all()
    identities = db.query(ExternalIdentity).filter(ExternalIdentity.user_id == current_user.id, ExternalIdentity.is_active == True).all()

    provenance = []
    for extraction in extractions:
        document = next((d for d in documents if d.id == extraction.document_id), None)
        provenance.append({
            "extraction_id": str(extraction.id),
            "document_id": str(extraction.document_id) if extraction.document_id else None,
            "document": document.original_filename if document else None,
            "status": extraction.status,
            "confidence": extraction.confidence_scores,
            "created_at": extraction.created_at,
        })

    return {
        "profile": {
            "id": str(profile.id),
            "full_name": profile.full_name,
            "location": profile.location,
            "title": profile.title,
            "summary": profile.summary,
            "primary_email": profile.primary_email,
            "primary_phone": profile.primary_phone,
            "linkedin_url": profile.linkedin_url,
            "years_experience": profile.years_experience,
            "industries": profile.industries or [],
            "seniority": profile.seniority,
            "work_preferences": profile.work_preferences or {},
            "reconciliation_status": profile.reconciliation_status,
        },
        "completeness": {
            "overall_score": calculate_completeness(profile.id, db),
            "breakdown": profile.completeness_breakdown or {},
        },
        "experience": [
            {
                "id": str(x.id), "company": x.company, "title": x.title,
                "location": x.location, "start_date": x.start_date, "end_date": x.end_date,
                "is_current": x.is_current, "responsibilities": x.responsibilities or [],
                "achievements": x.achievements or [], "source_type": x.source_type,
                "source_id": str(x.source_id) if x.source_id else None,
                "reconciliation_status": x.reconciliation_status,
            } for x in experiences
        ],
        "skills": [
            {
                "id": str(x.id), "name": x.name, "category": x.category,
                "proficiency": x.proficiency, "years_experience": x.years_experience,
                "confidence": x.confidence, "source_type": x.source_type,
                "source_id": str(x.source_id) if x.source_id else None,
            } for x in skills
        ],
        "certifications": [
            {
                "id": str(x.id), "name": x.name, "issuer": x.issuer,
                "issue_date": x.issue_date, "expiry_date": x.expiry_date,
                "credential_reference": x.credential_reference, "credential_url": x.credential_url,
                "confidence": x.confidence, "source_type": x.source_type,
                "source_id": str(x.source_id) if x.source_id else None,
            } for x in certifications
        ],
        "education": [
            {
                "id": str(x.id), "institution": x.institution, "degree": x.degree,
                "field_of_study": x.field_of_study, "start_date": x.start_date,
                "end_date": x.end_date, "grade": x.grade, "confidence": x.confidence,
                "source_type": x.source_type, "source_id": str(x.source_id) if x.source_id else None,
            } for x in educations
        ],
        "documents": [
            {
                "id": str(x.id), "original_filename": x.original_filename, "filename": x.filename,
                "category": x.document_category, "subcategory": x.document_subcategory,
                "status": x.status, "extraction_status": x.extraction_status,
                "classification_confidence": x.classification_confidence,
                "content_hash": x.content_hash, "batch_id": str(x.batch_id) if x.batch_id else None,
                "is_zip_content": x.is_zip_content, "parent_zip_id": str(x.parent_zip_id) if x.parent_zip_id else None,
                "source_metadata": x.source_metadata or {}, "created_at": x.created_at,
            } for x in documents
        ],
        "connections": [
            {
                "id": str(x.id), "provider": x.provider, "provider_email": x.provider_email,
                "scopes": x.scopes or [], "last_used": x.last_used,
            } for x in identities
        ],
        "provenance": provenance,
        "readiness": {
            "documents": len(documents),
            "processed_documents": sum(1 for x in documents if x.extraction_status == "complete"),
            "experiences": len(experiences),
            "skills": len(skills),
            "certifications": len(certifications),
            "education": len(educations),
            "oauth_connections": [x.provider for x in identities],
        },
    }
