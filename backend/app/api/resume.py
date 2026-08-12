from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.persona import Persona
from app.models.job import Job
from app.models.job_dna import JobDNA
from app.models.resume_version import ResumeVersion
from app.models.resume_section import ResumeSection
from app.models.resume_evidence_link import ResumeEvidenceLink
from app.models.career_profile import CareerProfile
from app.models.career_evidence import CareerEvidence
from app.schemas.resume import ResumeGenerateRequest, ResumeResponse, ResumeSectionResponse
from app.utils.resume_generator import ResumeGenerator

router = APIRouter(prefix="/resumes", tags=["resumes"])
resume_generator = ResumeGenerator()


@router.post("/generate", response_model=ResumeResponse)
async def generate_resume(
    request: ResumeGenerateRequest,
    db: Session = Depends(get_db)
):
    """Generate a JD-specific resume."""
    
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify persona exists
    persona = db.query(Persona).filter(Persona.id == request.persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    # Verify job exists and has DNA
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job_dna = db.query(JobDNA).filter(JobDNA.job_id == request.job_id).first()
    if not job_dna:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job DNA not found. Please analyze the job first."
        )
    
    # Get career vault data
    career_vault = {}
    if persona.career_profile_id:
        profile = db.query(CareerProfile).filter(
            CareerProfile.id == persona.career_profile_id
        ).first()
        if profile:
            career_vault = {
                "employments": profile.employments if profile.employments else [],
                "projects": profile.projects if profile.projects else [],
                "skills": profile.skills if profile.skills else [],
                "certifications": profile.certifications if profile.certifications else [],
                "educations": profile.educations if profile.educations else [],
                "achievements": profile.achievements if profile.achievements else [],
            }
    
    # Get existing resume versions
    existing_count = db.query(ResumeVersion).filter(
        ResumeVersion.user_id == request.user_id,
        ResumeVersion.job_id == request.job_id,
        ResumeVersion.persona_id == request.persona_id
    ).count()
    
    # Prepare persona data
    persona_data = {
        "name": persona.name,
        "description": persona.description,
        "target_titles": persona.target_titles,
        "skill_weights": persona.skill_weights or {},
    }
    
    # Prepare job DNA data
    job_dna_data = {
        "keywords": job_dna.keywords or [],
        "skills": job_dna.skills or {},
        "technologies": job_dna.technologies or [],
        "certifications_required": job_dna.certifications_required or {},
        "seniority": job_dna.seniority,
        "role_family": job_dna.role_family,
    }
    
    # Generate resume
    result = resume_generator.generate(career_vault, persona_data, job_dna_data)
    
    # Create resume version
    resume = ResumeVersion(
        user_id=request.user_id,
        job_id=request.job_id,
        persona_id=request.persona_id,
        version_number=existing_count + 1,
        content=result["content"],
        format_type=result["format_type"],
        ats_score=result["ats_score"],
        keyword_coverage=result["keyword_coverage"],
        truth_score=result["truth_score"],
        status="draft"
    )
    db.add(resume)
    db.flush()
    
    # Create resume sections
    for section_data in result["sections"]:
        section = ResumeSection(
            resume_id=resume.id,
            section_type=section_data["type"],
            section_title=section_data["title"],
            order=section_data["order"],
            content=section_data["content"],
            source_evidence=section_data.get("evidence", [])
        )
        db.add(section)
        db.flush()
        
        # Create evidence links
        for evidence_item in section_data.get("evidence", []):
            # Try to find existing evidence
            evidence = None
            if isinstance(evidence_item, dict):
                # Look for matching evidence
                evidence = db.query(CareerEvidence).filter(
                    CareerEvidence.claim == evidence_item.get("description", ""),
                    CareerEvidence.career_profile_id == persona.career_profile_id
                ).first()
            
            link = ResumeEvidenceLink(
                section_id=section.id,
                statement=section_data["content"][:500],  # First 500 chars
                evidence_id=evidence.id if evidence else None,
                source_type=section_data["type"],
                source_reference={"title": section_data["title"]},
                is_verified=evidence is not None,
                confidence=1.0 if evidence else 0.5,
                explanation="Evidence from career vault" if evidence else "Pending verification"
            )
            db.add(link)
    
    db.commit()
    db.refresh(resume)
    
    return ResumeResponse(
        id=resume.id,
        user_id=resume.user_id,
        job_id=resume.job_id,
        persona_id=resume.persona_id,
        version_number=resume.version_number,
        content=resume.content,
        format_type=resume.format_type,
        ats_score=resume.ats_score,
        keyword_coverage=resume.keyword_coverage,
        truth_score=resume.truth_score,
        status=resume.status,
        created_at=resume.created_at,
        updated_at=resume.updated_at
    )


@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    user_id: Optional[UUID] = None,
    job_id: Optional[UUID] = None,
    persona_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """List resumes for a user, job, or persona."""
    query = db.query(ResumeVersion)
    
    if user_id:
        query = query.filter(ResumeVersion.user_id == user_id)
    if job_id:
        query = query.filter(ResumeVersion.job_id == job_id)
    if persona_id:
        query = query.filter(ResumeVersion.persona_id == persona_id)
    
    resumes = query.order_by(ResumeVersion.created_at.desc()).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific resume."""
    resume = db.query(ResumeVersion).filter(ResumeVersion.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    return resume


@router.get("/{resume_id}/sections", response_model=List[ResumeSectionResponse])
async def get_resume_sections(
    resume_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all sections for a resume."""
    sections = db.query(ResumeSection).filter(
        ResumeSection.resume_id == resume_id
    ).order_by(ResumeSection.order).all()
    return sections


@router.get("/{resume_id}/preview")
async def preview_resume(
    resume_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a formatted preview of the resume."""
    resume = db.query(ResumeVersion).filter(ResumeVersion.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # In a real implementation, this would return HTML/PDF preview
    return {
        "content": resume.content,
        "format_type": resume.format_type,
        "ats_score": resume.ats_score,
        "truth_score": resume.truth_score
    }


@router.post("/{resume_id}/approve")
async def approve_resume(
    resume_id: UUID,
    db: Session = Depends(get_db)
):
    """Mark a resume as approved."""
    resume = db.query(ResumeVersion).filter(ResumeVersion.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    resume.status = "approved"
    resume.is_active = True
    db.commit()
    
    return {"message": "Resume approved successfully"}


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a resume."""
    resume = db.query(ResumeVersion).filter(ResumeVersion.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    db.delete(resume)
    db.commit()
    
    return None
