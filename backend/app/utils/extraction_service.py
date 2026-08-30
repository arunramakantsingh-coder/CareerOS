from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime

from app.utils.cv_parser import CVParser
from app.utils.document_processing import read_document_text
from app.models.extraction_result import ExtractionResult
from app.models.extraction_field import ExtractionField
from app.models.candidate_profile import CandidateProfile
from app.models.document import Document
from app.models.professional_experience import ProfessionalExperience
from app.models.candidate_skill import CandidateSkill
from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation


class ExtractionService:
    """Evidence-first document extraction service using the canonical candidate models."""

    def __init__(self):
        self.parser = CVParser()

    def extract_from_document(self, document: Document, db) -> ExtractionResult:
        text, method = read_document_text(document.storage_path)
        if not text.strip():
            raise ValueError('No readable text was found in the document')

        parsed_data = self.parser.parse(text, str(document.id))
        parsed_data['source'] = {
            'document_id': str(document.id),
            'filename': document.original_filename,
            'method': method,
            'extracted_at': datetime.utcnow().isoformat(),
        }

        extraction = ExtractionResult(
            candidate_id=document.candidate_id,
            document_id=document.id,
            extraction_type='professional_document',
            extraction_version='1.1',
            extracted_data=parsed_data,
            confidence_scores=self._extract_confidence(parsed_data),
            status='complete',
            is_reconciled=False,
        )
        db.add(extraction)
        db.flush()
        self._create_fields(extraction.id, parsed_data, db)
        document.extraction_status = 'complete'
        document.status = 'processed'
        document.extraction_id = extraction.id
        document.processing_status = {
            **(document.processing_status or {}),
            'stage': 'complete',
            'extraction_method': method,
            'extracted_at': datetime.utcnow().isoformat(),
        }
        db.commit()
        self._populate_profile(document.candidate_id, parsed_data, db)
        db.refresh(extraction)
        return extraction

    def _extract_confidence(self, parsed_data: Dict[str, Any]) -> Dict[str, float]:
        personal = parsed_data.get('personal', {})
        return {
            'personal': 0.95 if personal.get('email') or personal.get('name') else 0.2,
            'professional': min(len(parsed_data.get('professional', [])) * 0.2, 1.0),
            'skills': min(len(parsed_data.get('skills', [])) * 0.1, 1.0),
            'certifications': min(len(parsed_data.get('certifications', [])) * 0.2, 1.0),
            'education': min(len(parsed_data.get('education', [])) * 0.25, 1.0),
            'overall': float(parsed_data.get('confidence', 0.5)),
        }

    def _create_fields(self, extraction_id: UUID, parsed_data: Dict[str, Any], db) -> List[ExtractionField]:
        fields: List[ExtractionField] = []
        personal = parsed_data.get('personal', {})
        for key, value in personal.items():
            if value:
                fields.append(ExtractionField(extraction_id=extraction_id, field_key=f'personal.{key}', field_category='personal', value=str(value), value_type='string', confidence=0.9, extraction_status='extracted'))
        for skill in parsed_data.get('skills', []):
            if skill.get('name'):
                fields.append(ExtractionField(extraction_id=extraction_id, field_key=f"skill.{skill['name']}", field_category='skill', value=skill['name'], value_type='string', confidence=0.75, extraction_status='extracted'))
        for field in fields: db.add(field)
        return fields

    def _populate_profile(self, candidate_id: UUID, parsed_data: Dict[str, Any], db):
        profile = db.query(CandidateProfile).filter(CandidateProfile.id == candidate_id).first()
        if not profile: return
        personal = parsed_data.get('personal', {})

        # Evidence-derived values only fill empty canonical fields. Existing values are never silently overwritten.
        mappings = {'name': 'full_name', 'email': 'primary_email', 'phone': 'primary_phone', 'location': 'location', 'title': 'title', 'summary': 'summary', 'linkedin': 'linkedin_url'}
        for source_key, target in mappings.items():
            value = personal.get(source_key)
            if value and not getattr(profile, target, None): setattr(profile, target, value)

        for skill in parsed_data.get('skills', []):
            name = skill.get('name')
            if name and not db.query(CandidateSkill).filter(CandidateSkill.candidate_id == candidate_id, CandidateSkill.name.ilike(name)).first():
                db.add(CandidateSkill(candidate_id=candidate_id, name=name, category=skill.get('category', 'Technical'), confidence=0.75))

        for exp in parsed_data.get('professional', []):
            if exp.get('company') and exp.get('title'):
                existing = db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == candidate_id, ProfessionalExperience.company.ilike(exp['company']), ProfessionalExperience.title.ilike(exp['title'])).first()
                if not existing:
                    db.add(ProfessionalExperience(candidate_id=candidate_id, company=exp['company'], title=exp['title'], responsibilities=exp.get('responsibilities', []), achievements=exp.get('achievements', []), is_reconciled=False))

        for cert in parsed_data.get('certifications', []):
            name = cert.get('name')
            if name and not db.query(CandidateCertification).filter(CandidateCertification.candidate_id == candidate_id, CandidateCertification.name.ilike(name)).first():
                db.add(CandidateCertification(candidate_id=candidate_id, name=name, issuer=cert.get('issuer') or 'Unknown', confidence=cert.get('confidence', 0.7)))

        for edu in parsed_data.get('education', []):
            if edu.get('degree') and edu.get('institution') and not db.query(CandidateEducation).filter(CandidateEducation.candidate_id == candidate_id, CandidateEducation.institution.ilike(edu['institution']), CandidateEducation.degree.ilike(edu['degree'])).first():
                db.add(CandidateEducation(candidate_id=candidate_id, institution=edu['institution'], degree=edu['degree'], field_of_study=edu.get('field'), confidence=0.7))

        profile.reconciliation_status = 'review_required' if parsed_data.get('confidence', 0) < 0.75 else 'pending'
        db.commit()
