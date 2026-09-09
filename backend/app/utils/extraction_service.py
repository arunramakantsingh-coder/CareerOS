from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
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
    """Evidence-first document extraction and canonical fact reconciliation.

    The deterministic parser remains the precision-first baseline. This service is responsible
    for mapping parser output into canonical CareerOS facts while preserving provenance and an
    inspectable intermediate representation that the future Intelligence Engine can consume.
    """

    MONTHS = {
        "jan": 1,
        "january": 1,
        "feb": 2,
        "february": 2,
        "mar": 3,
        "march": 3,
        "apr": 4,
        "april": 4,
        "may": 5,
        "jun": 6,
        "june": 6,
        "jul": 7,
        "july": 7,
        "aug": 8,
        "august": 8,
        "sep": 9,
        "sept": 9,
        "september": 9,
        "oct": 10,
        "october": 10,
        "nov": 11,
        "november": 11,
        "dec": 12,
        "december": 12,
    }

    def __init__(self):
        self.parser = CVParser()

    def extract_from_document(self, document: Document, db) -> ExtractionResult:
        text = self._get_document_text(document)
        if not text.strip():
            raise ValueError("No extractable text was produced for this document")

        document.processing_stage = "extracting"
        document.processing_status = {
            **(document.processing_status or {}),
            "stage": "extracting",
        }
        db.commit()

        parsed = self.parser.parse(
            text,
            str(document.id),
            document.document_category,
        )

        # Persist a human-inspectable intermediate representation without creating a second
        # source of truth. The structured JSON mirrors parser output; Markdown is a presentation
        # of the same data for debugging and future AI/tool ingestion.
        representation = self._build_representation(parsed, document)
        document.source_metadata = {
            **(document.source_metadata or {}),
            "career_os_representation": representation,
        }

        extraction = ExtractionResult(
            candidate_id=document.candidate_id,
            document_id=document.id,
            extraction_type=document.document_category or "document",
            extraction_version="2.1",
            extracted_data=parsed,
            confidence_scores=self._extract_confidence(parsed),
            status="complete",
            is_reconciled=False,
        )
        db.add(extraction)
        db.flush()

        self._create_fields(extraction.id, parsed, document, db)
        self._populate_profile(document.candidate_id, parsed, document, db)

        document.detected_type = (
            f"{document.document_category}:{document.document_subcategory}"
            if document.document_subcategory
            else document.document_category
        )
        classification = (document.processing_status or {}).get("classification") or {}
        document.classification_reason = classification.get("reason")
        document.verification_status = "reported"
        document.processing_stage = "complete"
        document.extraction_id = extraction.id
        document.extraction_status = "complete"
        document.status = "processed"
        document.processing_status = {
            **(document.processing_status or {}),
            "stage": "complete",
            "extraction_id": str(extraction.id),
        }
        extraction.is_reconciled = True
        db.commit()
        db.refresh(extraction)
        return extraction

    def _get_document_text(self, document: Document) -> str:
        return (document.source_metadata or {}).get("extracted_text", "")

    def _extract_confidence(self, parsed: Dict[str, Any]) -> Dict[str, float]:
        values = {
            key: parsed.get(key, [])
            for key in ("professional", "skills", "certifications", "education")
        }
        return {
            **{
                key: min(0.98, 0.55 + 0.12 * min(len(value), 4))
                for key, value in values.items()
            },
            "personal": 0.82 if parsed.get("personal") else 0.2,
            "overall": parsed.get("confidence", 0.5),
        }

    def _create_fields(
        self,
        extraction_id: UUID,
        parsed: Dict[str, Any],
        document: Document,
        db,
    ) -> List[ExtractionField]:
        fields: List[ExtractionField] = []
        for key, value in (parsed.get("personal") or {}).items():
            if value:
                fields.append(
                    self._field(
                        extraction_id,
                        f"personal.{key}",
                        "personal",
                        value,
                        0.82,
                        document,
                    )
                )

        for skill in parsed.get("skills", []):
            if skill.get("name"):
                fields.append(
                    self._field(
                        extraction_id,
                        f"skill.{skill['name']}",
                        "skill",
                        skill["name"],
                        skill.get("confidence", 0.82),
                        document,
                    )
                )

        # Expose the structured non-personal facts in ExtractionField as well. This keeps the
        # extraction result independently inspectable before future LLM reconciliation is added.
        for index, exp in enumerate(parsed.get("professional", [])):
            if exp.get("company") or exp.get("title"):
                fields.append(
                    self._field(
                        extraction_id,
                        f"employment.{index}",
                        "employment",
                        self._json_value(exp),
                        exp.get("confidence", 0.78),
                        document,
                    )
                )

        for index, cert in enumerate(parsed.get("certifications", [])):
            if cert.get("name"):
                fields.append(
                    self._field(
                        extraction_id,
                        f"certification.{index}",
                        "certification",
                        self._json_value(cert),
                        cert.get("confidence", 0.88),
                        document,
                    )
                )

        for index, edu in enumerate(parsed.get("education", [])):
            if edu.get("degree") or edu.get("institution"):
                fields.append(
                    self._field(
                        extraction_id,
                        f"education.{index}",
                        "education",
                        self._json_value(edu),
                        edu.get("confidence", 0.9),
                        document,
                    )
                )

        for field in fields:
            db.add(field)
        return fields

    def _field(
        self,
        extraction_id,
        key,
        category,
        value,
        confidence,
        document,
    ):
        serialized = str(value)
        return ExtractionField(
            extraction_id=extraction_id,
            field_key=key,
            field_category=category,
            value=serialized,
            value_type="json" if category in {"employment", "certification", "education"} else "string",
            source_text=serialized,
            confidence=confidence,
            confidence_reason="Extracted from the matching document section",
            extraction_status="extracted",
            extraction_metadata={"document_id": str(document.id)},
        )

    def _populate_profile(
        self,
        candidate_id: UUID,
        parsed: Dict[str, Any],
        document: Document,
        db,
    ):
        profile = db.query(CandidateProfile).filter(CandidateProfile.id == candidate_id).first()
        if not profile:
            return

        personal = parsed.get("personal", {})
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

        for skill in parsed.get("skills", []):
            name = self._normalize_skill(skill.get("name", ""))
            if not name:
                continue
            existing = next(
                (
                    x
                    for x in db.query(CandidateSkill)
                    .filter(CandidateSkill.candidate_id == candidate_id)
                    .all()
                    if self._normalize_skill(x.name) == name
                ),
                None,
            )
            if not existing:
                existing = CandidateSkill(
                    candidate_id=candidate_id,
                    name=name,
                    category=skill.get("category", "Technical"),
                    confidence=skill.get("confidence", 0.82),
                    source_type="document",
                    source_id=document.id,
                )
                db.add(existing)
                db.flush()
            self._link(
                document,
                candidate_id,
                "skill",
                existing.id,
                skill.get("confidence", 0.82),
                skill.get("name"),
                db,
            )

        for exp in parsed.get("professional", []):
            company = (exp.get("company") or "").strip()
            title = (exp.get("title") or "").strip()
            if not company or not title:
                continue
            existing = (
                db.query(ProfessionalExperience)
                .filter(
                    ProfessionalExperience.candidate_id == candidate_id,
                    ProfessionalExperience.company.ilike(company),
                    ProfessionalExperience.title.ilike(title),
                )
                .first()
            )
            if not existing:
                existing = ProfessionalExperience(
                    candidate_id=candidate_id,
                    company=company,
                    title=title,
                    responsibilities=exp.get("responsibilities", []),
                    achievements=exp.get("achievements", []),
                    is_reconciled=False,
                    reconciliation_status="extracted",
                    source_type="document",
                    source_id=document.id,
                    start_date=self._date(exp.get("start_date")),
                    end_date=self._date(exp.get("end_date")),
                    is_current=bool(exp.get("is_current")),
                )
                db.add(existing)
                db.flush()
            else:
                # Preserve existing canonical data, but enrich empty structured fields from a
                # new supporting document. Never silently overwrite populated values.
                if not existing.responsibilities and exp.get("responsibilities"):
                    existing.responsibilities = exp.get("responsibilities")
                if not existing.achievements and exp.get("achievements"):
                    existing.achievements = exp.get("achievements")
                if not existing.start_date and exp.get("start_date"):
                    existing.start_date = self._date(exp.get("start_date"))
                if not existing.end_date and exp.get("end_date"):
                    existing.end_date = self._date(exp.get("end_date"))
                if not existing.is_current and exp.get("is_current"):
                    existing.is_current = True
            self._link(
                document,
                candidate_id,
                "employment",
                existing.id,
                exp.get("confidence", 0.78),
                self._employment_excerpt(exp),
                db,
            )

        for cert in parsed.get("certifications", []):
            name = (cert.get("name") or "").strip()
            if not name:
                continue
            issuer = (cert.get("issuer") or "Unknown").strip()
            existing = next(
                (
                    x
                    for x in db.query(CandidateCertification)
                    .filter(CandidateCertification.candidate_id == candidate_id)
                    .all()
                    if self._same_cert(x, name, issuer)
                ),
                None,
            )
            if not existing:
                existing = CandidateCertification(
                    candidate_id=candidate_id,
                    name=name,
                    issuer=issuer,
                    issue_date=self._date(cert.get("issue_date")),
                    expiry_date=self._date(cert.get("expiry_date")),
                    credential_reference=cert.get("credential_reference"),
                    confidence=cert.get("confidence", 0.88),
                    source_type="document",
                    source_id=document.id,
                )
                db.add(existing)
                db.flush()
            self._link(
                document,
                candidate_id,
                "certification",
                existing.id,
                cert.get("confidence", 0.88),
                name,
                db,
            )

        for edu in parsed.get("education", []):
            degree = (edu.get("degree") or "").strip()
            institution = (edu.get("institution") or "").strip()
            if not degree or not institution:
                continue
            existing = next(
                (
                    x
                    for x in db.query(CandidateEducation)
                    .filter(CandidateEducation.candidate_id == candidate_id)
                    .all()
                    if self._norm(x.degree) == self._norm(degree)
                    and self._norm(x.institution) == self._norm(institution)
                ),
                None,
            )
            if not existing:
                existing = CandidateEducation(
                    candidate_id=candidate_id,
                    institution=institution,
                    degree=degree,
                    field_of_study=edu.get("field"),
                    confidence=edu.get("confidence", 0.9),
                    source_type="document",
                    source_id=document.id,
                    start_date=self._date(edu.get("start_date")),
                    end_date=self._date(edu.get("end_date")),
                    is_current=False,
                )
                db.add(existing)
                db.flush()
            self._link(
                document,
                candidate_id,
                "education",
                existing.id,
                edu.get("confidence", 0.9),
                f"{degree} — {institution}",
                db,
            )

        profile.reconciliation_status = "complete"
        profile.completeness_score = self._completeness(profile, db)

    def _link(self, document, candidate_id, fact_type, fact_id, confidence, excerpt, db):
        exists = (
            db.query(CareerFactEvidence)
            .filter(
                CareerFactEvidence.candidate_id == candidate_id,
                CareerFactEvidence.document_id == document.id,
                CareerFactEvidence.fact_type == fact_type,
                CareerFactEvidence.fact_id == fact_id,
            )
            .first()
        )
        if not exists:
            db.add(
                CareerFactEvidence(
                    candidate_id=candidate_id,
                    document_id=document.id,
                    fact_type=fact_type,
                    fact_id=fact_id,
                    relationship="supports",
                    confidence=confidence,
                    excerpt=str(excerpt)[:1000] if excerpt else None,
                )
            )

    def _same_cert(self, item, name, issuer):
        return (
            self._norm(item.name) == self._norm(name)
            and (
                self._norm(item.issuer) == self._norm(issuer)
                or self._norm(item.issuer) in {"", "unknown"}
                or self._norm(issuer) in {"", "unknown"}
            )
        )

    def _normalize_skill(self, name):
        aliases = {
            "ms azure": "Microsoft Azure",
            "microsoft azure": "Microsoft Azure",
            "amazon web services": "AWS",
            "amazon aws": "AWS",
            "google cloud platform": "Google Cloud Platform",
        }
        return aliases.get(self._norm(name), name.strip()) if name else ""

    def _norm(self, value):
        return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()

    def _date(self, value) -> Optional[datetime]:
        """Parse common CV date formats without collapsing month precision to January.

        Accepted forms include ISO dates, month/year ("Aug 2025"), year-only values and the
        parser's existing YYYY-MM-DD strings. A bare year remains normalized to January 1 because
        the source did not establish a more precise month.
        """
        if not value:
            return None
        if isinstance(value, datetime):
            return value

        raw = str(value).strip()
        if raw.lower() in {"present", "current", "now", "ongoing"}:
            return None

        iso = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", raw)
        if iso:
            try:
                return datetime(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
            except ValueError:
                return None

        month_year = re.search(
            r"\b(" + "|".join(self.MONTHS.keys()) + r")\.?\s+(\d{4})\b",
            raw,
            re.I,
        )
        if not month_year:
            month_year = re.search(
                r"\b(\d{4})\s+(-|/)?\s*(" + "|".join(self.MONTHS.keys()) + r")\.?\b",
                raw,
                re.I,
            )
            if month_year:
                year = int(month_year.group(1))
                month = self.MONTHS[month_year.group(3).lower().rstrip(".")]
            else:
                year_match = re.search(r"\b(19|20)\d{2}\b", raw)
                if not year_match:
                    return None
                return datetime(int(year_match.group(0)), 1, 1)
        else:
            month = self.MONTHS[month_year.group(1).lower().rstrip(".")]
            year = int(month_year.group(2))

        return datetime(year, month, 1)

    def _employment_excerpt(self, exp: Dict[str, Any]) -> str:
        parts = [exp.get("title"), exp.get("company")]
        parts.extend(exp.get("responsibilities") or [])
        parts.extend(exp.get("achievements") or [])
        return " | ".join(str(part) for part in parts if part)

    def _json_value(self, value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, default=str, sort_keys=True)

    def _build_representation(self, parsed: Dict[str, Any], document: Document) -> Dict[str, Any]:
        normalized = {
            "schema_version": "career-os.document-representation.v1",
            "document_id": str(document.id),
            "document_category": document.document_category,
            "document_subcategory": document.document_subcategory,
            "source": {
                "filename": document.original_filename,
                "mime_type": document.mime_type,
                "content_hash": document.content_hash,
            },
            "personal": parsed.get("personal", {}),
            "employment": parsed.get("professional", []),
            "skills": parsed.get("skills", []),
            "certifications": parsed.get("certifications", []),
            "education": parsed.get("education", []),
            "projects": parsed.get("projects", []),
            "achievements": parsed.get("achievements", []),
            "trust": {
                "state": "EXTRACTED",
                "confidence": parsed.get("confidence", 0.5),
                "requires_confirmation": False,
            },
        }
        markdown_lines = [
            f"# CareerOS Document Representation",
            f"- Document ID: `{document.id}`",
            f"- Category: `{document.document_category or 'unknown'}`",
            f"- Original file: `{document.original_filename}`",
            "",
        ]
        if normalized["personal"]:
            markdown_lines.append("## Personal")
            for key, value in normalized["personal"].items():
                markdown_lines.append(f"- **{key}**: {value}")
            markdown_lines.append("")
        if normalized["employment"]:
            markdown_lines.append("## Employment")
            for item in normalized["employment"]:
                markdown_lines.append(
                    f"### {item.get('title') or 'Role'} — {item.get('company') or 'Unknown employer'}"
                )
                markdown_lines.append(
                    f"- Dates: {item.get('start_date') or 'unknown'} → {item.get('end_date') or 'present/unknown'}"
                )
                for responsibility in item.get("responsibilities") or []:
                    markdown_lines.append(f"- Responsibility: {responsibility}")
                for achievement in item.get("achievements") or []:
                    markdown_lines.append(f"- Achievement: {achievement}")
            markdown_lines.append("")
        if normalized["skills"]:
            markdown_lines.append("## Skills")
            markdown_lines.extend(f"- {item.get('name')}" for item in normalized["skills"] if item.get("name"))
            markdown_lines.append("")
        if normalized["certifications"]:
            markdown_lines.append("## Certifications")
            markdown_lines.extend(f"- {item.get('name')}" for item in normalized["certifications"] if item.get("name"))
            markdown_lines.append("")
        if normalized["education"]:
            markdown_lines.append("## Education")
            markdown_lines.extend(
                f"- {item.get('degree')} — {item.get('institution')}"
                for item in normalized["education"]
                if item.get("degree") or item.get("institution")
            )
            markdown_lines.append("")

        normalized["markdown"] = "\n".join(markdown_lines).strip() + "\n"
        normalized["json"] = self._json_value(normalized)
        return normalized

    def _completeness(self, profile, db):
        checks = [
            bool(profile.full_name),
            bool(profile.location),
            bool(profile.title),
            bool(profile.summary),
            db.query(ProfessionalExperience)
            .filter(ProfessionalExperience.candidate_id == profile.id)
            .count()
            > 0,
            db.query(CandidateEducation)
            .filter(CandidateEducation.candidate_id == profile.id)
            .count()
            > 0,
            db.query(CandidateCertification)
            .filter(CandidateCertification.candidate_id == profile.id)
            .count()
            > 0,
            db.query(CandidateSkill)
            .filter(CandidateSkill.candidate_id == profile.id)
            .count()
            > 0,
        ]
        return round(sum(checks) / len(checks) * 100, 1)
