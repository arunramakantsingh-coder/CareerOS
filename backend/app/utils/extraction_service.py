from typing import Dict, Any, Optional, List
from uuid import UUID
import json
from datetime import datetime

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
    """Service for extracting profile data from documents."""
    
    def __init__(self):
        self.parser = CVParser()
    
    def extract_from_document(self, document: Document, db) -> ExtractionResult:
        """Extract profile data from a document."""
        
        # In production, this would read the actual file content
        # For now, we'll simulate with the document metadata
        text = self._get_document_text(document, db)
        
        # Parse the text
        parsed_data = self.parser.parse(text, str(document.id))
        
        # Create extraction result
        extraction = ExtractionResult(
            candidate_id=document.candidate_id,
            document_id=document.id,
            extraction_type="cv",
            extraction_version="1.0",
            extracted_data=parsed_data,
            confidence_scores=self._extract_confidence(parsed_data),
            status="complete",
            is_reconciled=False
        )
        db.add(extraction)
        db.flush()
        
        # Create extraction fields
        fields = self._create_fields(extraction.id, parsed_data, db)
        
        # Update document status
        document.extraction_status = "complete"
        document.status = "processed"
        db.commit()
        
        # Auto-populate profile from extraction
        self._populate_profile(document.candidate_id, parsed_data, db)
        
        db.refresh(extraction)
        return extraction
    
    def _get_document_text(self, document: Document, db) -> str:
        """Get text content from a document."""
        # In production, this would read from storage
        # For now, return a sample CV text
        return """
        John Smith
        Senior Network Architect
        
        Email: john.smith@example.com
        Phone: +1 555-123-4567
        LinkedIn: linkedin.com/in/johnsmith
        
        Summary:
        Senior Network Architect with 10+ years of experience in designing and implementing secure enterprise networks. Expert in routing, switching, and network security.
        
        Experience:
        
        Senior Network Architect | TechCorp Inc.
        2020 - Present
        • Designed and implemented multi-site SD-WAN architecture
        • Led network security transformation initiative
        • Achieved 99.99% uptime across global network
        
        Network Engineer | DataSphere Solutions
        2017 - 2020
        • Managed network infrastructure across 50+ locations
        • Implemented zero-trust security framework
        • Reduced network incidents by 40%
        
        Skills:
        Routing, Switching, SD-WAN, Firewall, Zero Trust, AWS, Azure, Python
        
        Certifications:
        CISSP - 2020
        CCIE - 2019
        
        Education:
        M.S. Computer Science, Stanford University
        2015 - 2017
        """
    
    def _extract_confidence(self, parsed_data: Dict) -> Dict:
        """Extract confidence scores from parsed data."""
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
            "overall": parsed_data.get("confidence", 0.5)
        }
    
    def _create_fields(self, extraction_id: UUID, parsed_data: Dict, db) -> List[ExtractionField]:
        """Create extraction fields from parsed data."""
        fields = []
        
        # Personal fields
        personal = parsed_data.get("personal", {})
        for key, value in personal.items():
            if value:
                field = ExtractionField(
                    extraction_id=extraction_id,
                    field_key=f"personal.{key}",
                    field_category="personal",
                    value=str(value),
                    value_type="string",
                    confidence=0.8,
                    extraction_status="extracted"
                )
                db.add(field)
                fields.append(field)
        
        # Skills
        for skill in parsed_data.get("skills", []):
            if skill.get("name"):
                field = ExtractionField(
                    extraction_id=extraction_id,
                    field_key=f"skill.{skill['name']}",
                    field_category="skill",
                    value=skill["name"],
                    value_type="string",
                    confidence=0.7,
                    extraction_status="extracted"
                )
                db.add(field)
                fields.append(field)
        
        return fields
    
    def _populate_profile(self, candidate_id: UUID, parsed_data: Dict, db):
        """Auto-populate candidate profile from extraction."""
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.id == candidate_id
        ).first()
        
        if not profile:
            return
        
        personal = parsed_data.get("personal", {})
        
        # Update profile fields
        if personal.get("name") and not profile.full_name:
            profile.full_name = personal.get("name")
        if personal.get("email") and not profile.primary_email:
            profile.primary_email = personal.get("email")
        if personal.get("phone") and not profile.primary_phone:
            profile.primary_phone = personal.get("phone")
        if personal.get("location") and not profile.location:
            profile.location = personal.get("location")
        if personal.get("title") and not profile.title:
            profile.title = personal.get("title")
        if personal.get("summary") and not profile.summary:
            profile.summary = personal.get("summary")
        if personal.get("linkedin") and not profile.linkedin_url:
            profile.linkedin_url = personal.get("linkedin")
        
        db.commit()
        
        # Add skills
        for skill in parsed_data.get("skills", []):
            if skill.get("name"):
                existing = db.query(CandidateSkill).filter(
                    CandidateSkill.candidate_id == candidate_id,
                    CandidateSkill.name.ilike(skill["name"])
                ).first()
                if not existing:
                    cs = CandidateSkill(
                        candidate_id=candidate_id,
                        name=skill["name"],
                        category=skill.get("category", "Technical"),
                        confidence=0.7
                    )
                    db.add(cs)
        
        # Add experiences
        for exp in parsed_data.get("professional", []):
            if exp.get("company") and exp.get("title"):
                existing = db.query(ProfessionalExperience).filter(
                    ProfessionalExperience.candidate_id == candidate_id,
                    ProfessionalExperience.company.ilike(exp["company"])
                ).first()
                if not existing:
                    pe = ProfessionalExperience(
                        candidate_id=candidate_id,
                        company=exp["company"],
                        title=exp["title"],
                        responsibilities=exp.get("responsibilities", []),
                        achievements=exp.get("achievements", []),
                        is_reconciled=False
                    )
                    db.add(pe)
        
        # Add certifications
        for cert in parsed_data.get("certifications", []):
            if cert.get("name"):
                existing = db.query(CandidateCertification).filter(
                    CandidateCertification.candidate_id == candidate_id,
                    CandidateCertification.name.ilike(cert["name"])
                ).first()
                if not existing:
                    cc = CandidateCertification(
                        candidate_id=candidate_id,
                        name=cert["name"],
                        issuer=cert.get("issuer", "Unknown"),
                        confidence=cert.get("confidence", 0.7)
                    )
                    db.add(cc)
        
        # Add education
        for edu in parsed_data.get("education", []):
            if edu.get("degree") and edu.get("institution"):
                existing = db.query(CandidateEducation).filter(
                    CandidateEducation.candidate_id == candidate_id,
                    CandidateEducation.institution.ilike(edu["institution"])
                ).first()
                if not existing:
                    ce = CandidateEducation(
                        candidate_id=candidate_id,
                        institution=edu["institution"],
                        degree=edu["degree"],
                        field_of_study=edu.get("field"),
                        confidence=0.7
                    )
                    db.add(ce)
        
        db.commit()
