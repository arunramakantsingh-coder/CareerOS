from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.career_fact_evidence import CareerFactEvidence
from app.models.document import Document
from app.models.extraction_field import ExtractionField
from app.models.extraction_result import ExtractionResult
from app.models.professional_experience import ProfessionalExperience
from app.utils.cv_parser import CVParser


class ExtractionService:
    """Evidence-first document extraction and canonical fact reconciliation."""

    def __init__(self):
        self.parser = CVParser()

    def extract_from_document(self, document: Document, db) -> ExtractionResult:
        text = self._get_document_text(document)
        if not text.strip():
            raise ValueError("No extractable text was produced for this document")
        document.processing_stage = "extracting"
        document.processing_status = {**(document.processing_status or {}), "stage": "extracting"}
        db.commit()

        parsed = self.parser.parse(text, str(document.id), document.document_category)
        extraction = ExtractionResult(
            candidate_id=document.candidate_id,
            document_id=document.id,
            extraction_type=document.document_category or "document",
            extraction_version="2.0",
            extracted_data=parsed,
            confidence_scores=self._extract_confidence(parsed),
            status="complete",
            is_reconciled=False,
        )
        db.add(extraction)
        db.flush()
        self._create_fields(extraction.id, parsed, document, db)
        self._populate_profile(document.candidate_id, parsed, document, db)

        document.detected_type = f"{document.document_category}:{document.document_subcategory}" if document.document_subcategory else document.document_category
        classification = (document.processing_status or {}).get("classification") or {}
        document.classification_reason = classification.get("reason")
        document.verification_status = "reported"
        document.processing_stage = "complete"
        document.extraction_id = extraction.id
        document.extraction_status = "complete"
        document.status = "processed"
        document.processing_status = {**(document.processing_status or {}), "stage": "complete", "extraction_id": str(extraction.id)}
        extraction.is_reconciled = True
        db.commit()
        db.refresh(extraction)
        return extraction

    def _get_document_text(self, document: Document) -> str:
        return (document.source_metadata or {}).get("extracted_text", "")

    def _extract_confidence(self, parsed: Dict[str, Any]) -> Dict[str, float]:
        values = {k: parsed.get(k, []) for k in ("professional", "skills", "certifications", "education")}
        return {**{k: min(0.98, 0.55 + 0.12 * min(len(v), 4)) for k, v in values.items()}, "personal": 0.82 if parsed.get("personal") else 0.2, "overall": parsed.get("confidence", 0.5)}

    def _create_fields(self, extraction_id: UUID, parsed: Dict[str, Any], document: Document, db) -> List[ExtractionField]:
        fields: List[ExtractionField] = []
        for key, value in (parsed.get("personal") or {}).items():
            if value:
                fields.append(self._field(extraction_id, f"personal.{key}", "personal", value, 0.82, document))
        for skill in parsed.get("skills", []):
            if skill.get("name"):
                fields.append(self._field(extraction_id, f"skill.{skill['name']}", "skill", skill["name"], skill.get("confidence", 0.82), document))
        for field in fields: db.add(field)
        return fields

    def _field(self, extraction_id, key, category, value, confidence, document):
        return ExtractionField(
            extraction_id=extraction_id, field_key=key, field_category=category, value=str(value), value_type="string",
            source_text=str(value), confidence=confidence, confidence_reason="Extracted from the matching document section",
            extraction_status="extracted", extraction_metadata={"document_id": str(document.id)},
        )

    def _populate_profile(self, candidate_id: UUID, parsed: Dict[str, Any], document: Document, db):
        profile = db.query(CandidateProfile).filter(CandidateProfile.id == candidate_id).first()
        if not profile: return
        personal = parsed.get("personal", {})
        mappings = {"full_name": personal.get("name"), "primary_email": personal.get("email"), "primary_phone": personal.get("phone"), "location": personal.get("location"), "title": personal.get("title"), "summary": personal.get("summary"), "linkedin_url": personal.get("linkedin")}
        for field_name, value in mappings.items():
            if value and not getattr(profile, field_name, None): setattr(profile, field_name, value)

        for skill in parsed.get("skills", []):
            name = self._normalize_skill(skill.get("name", ""))
            if not name: continue
            existing = next((x for x in db.query(CandidateSkill).filter(CandidateSkill.candidate_id == candidate_id).all() if self._normalize_skill(x.name) == name), None)
            if not existing:
                existing = CandidateSkill(candidate_id=candidate_id, name=name, category=skill.get("category", "Technical"), confidence=skill.get("confidence", 0.82), source_type="document", source_id=document.id)
                db.add(existing); db.flush()
            self._link(document, candidate_id, "skill", existing.id, skill.get("confidence", 0.82), skill.get("name"), db)

        for exp in parsed.get("professional", []):
            company, title = (exp.get("company") or "").strip(), (exp.get("title") or "").strip()
            if not company or not title: continue
            existing = db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == candidate_id, ProfessionalExperience.company.ilike(company), ProfessionalExperience.title.ilike(title)).first()
            if not existing:
                existing = ProfessionalExperience(candidate_id=candidate_id, company=company, title=title, responsibilities=exp.get("responsibilities", []), achievements=exp.get("achievements", []), is_reconciled=False, reconciliation_status="extracted", source_type="document", source_id=document.id, start_date=self._date(exp.get("start_date")), end_date=self._date(exp.get("end_date")), is_current=bool(exp.get("is_current")))
                db.add(existing); db.flush()
            self._link(document, candidate_id, "employment", existing.id, exp.get("confidence", 0.78), title, db)

        for cert in parsed.get("certifications", []):
            name = (cert.get("name") or "").strip()
            if not name: continue
            issuer = (cert.get("issuer") or "Unknown").strip()
            existing = next((x for x in db.query(CandidateCertification).filter(CandidateCertification.candidate_id == candidate_id).all() if self._same_cert(x, name, issuer)), None)
            if not existing:
                existing = CandidateCertification(candidate_id=candidate_id, name=name, issuer=issuer, issue_date=self._date(cert.get("issue_date")), expiry_date=self._date(cert.get("expiry_date")), credential_reference=cert.get("credential_reference"), confidence=cert.get("confidence", 0.88), source_type="document", source_id=document.id)
                db.add(existing); db.flush()
            self._link(document, candidate_id, "certification", existing.id, cert.get("confidence", 0.88), name, db)

        for edu in parsed.get("education", []):
            degree, institution = (edu.get("degree") or "").strip(), (edu.get("institution") or "").strip()
            if not degree or not institution: continue
            existing = next((x for x in db.query(CandidateEducation).filter(CandidateEducation.candidate_id == candidate_id).all() if self._norm(x.degree) == self._norm(degree) and self._norm(x.institution) == self._norm(institution)), None)
            if not existing:
                existing = CandidateEducation(candidate_id=candidate_id, institution=institution, degree=degree, field_of_study=edu.get("field"), confidence=edu.get("confidence", 0.9), source_type="document", source_id=document.id, start_date=self._date(edu.get("start_date")), end_date=self._date(edu.get("end_date")), is_current=False)
                db.add(existing); db.flush()
            self._link(document, candidate_id, "education", existing.id, edu.get("confidence", 0.9), degree, db)
        profile.reconciliation_status = "complete"
        profile.completeness_score = self._completeness(profile, db)

    def _link(self, document, candidate_id, fact_type, fact_id, confidence, excerpt, db):
        exists = db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id == candidate_id, CareerFactEvidence.document_id == document.id, CareerFactEvidence.fact_type == fact_type, CareerFactEvidence.fact_id == fact_id).first()
        if not exists:
            db.add(CareerFactEvidence(candidate_id=candidate_id, document_id=document.id, fact_type=fact_type, fact_id=fact_id, relationship="supports", confidence=confidence, excerpt=str(excerpt)[:1000] if excerpt else None))

    def _same_cert(self, item, name, issuer):
        return self._norm(item.name) == self._norm(name) and (self._norm(item.issuer) == self._norm(issuer) or self._norm(item.issuer) in {"", "unknown"} or self._norm(issuer) in {"", "unknown"})

    def _normalize_skill(self, name):
        aliases = {"ms azure": "Microsoft Azure", "microsoft azure": "Microsoft Azure", "amazon web services": "AWS", "amazon aws": "AWS", "google cloud platform": "Google Cloud Platform"}
        return aliases.get(self._norm(name), name.strip()) if name else ""

    def _norm(self, value): return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()
    def _date(self, value):
        if not value: return None
        if isinstance(value, datetime): return value
        match = re.search(r"\b(19|20)\d{2}\b", str(value))
        return datetime(int(match.group(0)), 1, 1) if match else None

    def _completeness(self, profile, db):
        checks = [bool(profile.full_name), bool(profile.location), bool(profile.title), bool(profile.summary), db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == profile.id).count() > 0, db.query(CandidateEducation).filter(CandidateEducation.candidate_id == profile.id).count() > 0, db.query(CandidateCertification).filter(CandidateCertification.candidate_id == profile.id).count() > 0, db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id).count() > 0]
        return round(sum(checks) / len(checks) * 100, 1)
