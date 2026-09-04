from typing import Dict, Any, List
from uuid import UUID

from app.utils.cv_parser import CVParser
from app.models.extraction_result import ExtractionResult
from app.models.extraction_field import ExtractionField
from app.models.candidate_profile import CandidateProfile
from app.models.document import Document
from app.models.professional_experience import ProfessionalExperience
from app.models.candidate_skill import CandidateSkill
from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation


class ExtractionService:
    """Evidence-first extraction service.

    Important M02 rule: only documents explicitly classified as CV/resume may
    enrich the canonical professional profile. Other documents are evidence
    and are indexed, classified and OCR/text extracted, but never copied into
    profile sections automatically.
    """

    def __init__(self):
        self.parser = CVParser()

    def extract_from_document(self, document: Document, db) -> ExtractionResult:
        text = self._get_document_text(document)
        if not text.strip():
            raise ValueError("No extractable text was produced for this document")

        parsed_data = self.parser.parse(text, str(document.id))
        is_cv = (document.document_category or "").lower() == "cv"
        extraction_type = "cv_profile" if is_cv else "document_evidence"

        extraction = ExtractionResult(
            candidate_id=document.candidate_id,
            document_id=document.id,
            extraction_type=extraction_type,
            extraction_version="1.2",
            extracted_data=parsed_data,
            confidence_scores=self._extract_confidence(parsed_data),
            status="complete",
            is_reconciled=False,
        )
        db.add(extraction)
        db.flush()
        self._create_fields(extraction.id, parsed_data, document, db)
        document.extraction_id = extraction.id
        document.extraction_status = "complete"
        document.status = "processed"
        document.processing_status = {
            **(document.processing_status or {}),
            "stage": "profile_enriched" if is_cv else "evidence_indexed",
            "extraction_id": str(extraction.id),
            "profile_enrichment": "enabled" if is_cv else "disabled_non_cv_source",
        }
        db.commit()

        # Never let certificates, education, employment letters, payslips,
        # projects, etc. contaminate the canonical profile. They remain
        # evidence and can be reviewed/linked explicitly later.
        if is_cv:
            self._populate_profile(document.candidate_id, parsed_data, document, db)

        db.refresh(extraction)
        return extraction

    def _get_document_text(self, document: Document) -> str:
        source = document.source_metadata or {}
        return source.get("extracted_text", "")

    def _extract_confidence(self, parsed_data: Dict[str, Any]) -> Dict[str, float]:
        personal = parsed_data.get("personal", {})
        skills = parsed_data.get("skills", [])
        experiences = parsed_data.get("professional", [])
        certifications = parsed_data.get("certifications", [])
        education = parsed_data.get("education", [])
        return {
            "personal": 0.8 if any(personal.values()) else 0.2,
            "professional": min(len(experiences) * 0.2, 1.0),
            "skills": min(len(skills) * 0.1, 1.0),
            "certifications": min(len(certifications) * 0.2, 1.0),
            "education": min(len(education) * 0.25, 1.0),
            "overall": parsed_data.get("confidence", 0.5),
        }

    def _create_fields(self, extraction_id: UUID, parsed_data: Dict[str, Any], document: Document, db) -> List[ExtractionField]:
        fields: List[ExtractionField] = []
        personal = parsed_data.get("personal", {})
        for key, value in personal.items():
            if value:
                field = ExtractionField(
                    extraction_id=extraction_id,
                    field_key=f"personal.{key}",
                    field_category="personal",
                    value=str(value),
                    value_type="string",
                    source_text=str(value),
                    confidence=0.8,
                    confidence_reason="Extracted from source document",
                    extraction_status="extracted",
                    extraction_metadata={"document_id": str(document.id), "source_category": document.document_category},
                )
                db.add(field)
                fields.append(field)
        for skill in parsed_data.get("skills", []):
            if skill.get("name"):
                field = ExtractionField(
                    extraction_id=extraction_id,
                    field_key=f"skill.{skill['name']}",
                    field_category="skill",
                    value=skill["name"],
                    value_type="string",
                    source_text=skill["name"],
                    confidence=skill.get("confidence", 0.7),
                    confidence_reason="Matched against document skill vocabulary",
                    extraction_status="extracted",
                    extraction_metadata={"document_id": str(document.id), "source_category": document.document_category},
                )
                db.add(field)
                fields.append(field)
        return fields

    def _populate_profile(self, candidate_id: UUID, parsed_data: Dict[str, Any], document: Document, db):
        profile = db.query(CandidateProfile).filter(CandidateProfile.id == candidate_id).first()
        if not profile:
            return
        personal = parsed_data.get("personal", {})
        mappings = {
            "full_name": personal.get("name"),
            "primary_email": personal.get("email"),
            "primary_phone": personal.get("phone"),
            "location": personal.get("location"),
            "title": personal.get("title"),
            "summary": personal.get("summary"),
            "linkedin_url": personal.get("linkedin"),
        }
        for field_name, value in mappings.items():
            if value and not getattr(profile, field_name, None):
                setattr(profile, field_name, value)

        for skill in parsed_data.get("skills", []):
            if not skill.get("name"):
                continue
            existing = db.query(CandidateSkill).filter(
                CandidateSkill.candidate_id == candidate_id,
                CandidateSkill.name.ilike(skill["name"]),
            ).first()
            if not existing:
                db.add(CandidateSkill(
                    candidate_id=candidate_id,
                    name=skill["name"],
                    category=skill.get("category", "Technical"),
                    confidence=skill.get("confidence", 0.7),
                    source_type="cv",
                    source_id=document.id,
                ))

        for exp in parsed_data.get("professional", []):
            if not exp.get("company") or not exp.get("title"):
                continue
            existing = db.query(ProfessionalExperience).filter(
                ProfessionalExperience.candidate_id == candidate_id,
                ProfessionalExperience.company.ilike(exp["company"]),
                ProfessionalExperience.title.ilike(exp["title"]),
            ).first()
            if not existing:
                db.add(ProfessionalExperience(
                    candidate_id=candidate_id,
                    company=exp["company"],
                    title=exp["title"],
                    responsibilities=exp.get("responsibilities", []),
                    achievements=exp.get("achievements", []),
                    is_reconciled=False,
                    reconciliation_status="extracted_from_cv",
                    source_type="cv",
                    source_id=document.id,
                ))

        for cert in parsed_data.get("certifications", []):
            if not cert.get("name"):
                continue
            existing = db.query(CandidateCertification).filter(
                CandidateCertification.candidate_id == candidate_id,
                CandidateCertification.name.ilike(cert["name"]),
            ).first()
            if not existing:
                db.add(CandidateCertification(
                    candidate_id=candidate_id,
                    name=cert["name"],
                    issuer=cert.get("issuer") or "Unknown",
                    confidence=cert.get("confidence", 0.7),
                    source_type="cv",
                    source_id=document.id,
                ))

        for edu in parsed_data.get("education", []):
            if not edu.get("degree") or not edu.get("institution"):
                continue
            existing = db.query(CandidateEducation).filter(
                CandidateEducation.candidate_id == candidate_id,
                CandidateEducation.institution.ilike(edu["institution"]),
                CandidateEducation.degree.ilike(edu["degree"]),
            ).first()
            if not existing:
                db.add(CandidateEducation(
                    candidate_id=candidate_id,
                    institution=edu["institution"],
                    degree=edu["degree"],
                    field_of_study=edu.get("field"),
                    confidence=edu.get("confidence", 0.7),
                    source_type="cv",
                    source_id=document.id,
                ))

        profile.reconciliation_status = "in_progress"
        db.commit()
