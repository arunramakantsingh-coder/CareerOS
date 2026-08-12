from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job import Job
from app.models.job_dna import JobDNA
from app.models.job_skill import JobSkill
from app.models.job_responsibility import JobResponsibility
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobDNAResponse
from app.utils.jd_parser import JDParser
from app.utils.job_dna_generator import JobDNAGenerator

router = APIRouter(prefix="/jobs", tags=["jobs"])
parser = JDParser()
dna_generator = JobDNAGenerator()


@router.post("/analyze", response_model=JobDNAResponse)
async def analyze_job(
    job_data: JobCreate,
    db: Session = Depends(get_db)
):
    """Analyze a job description and generate Job DNA."""
    
    # Parse the job description
    parsed_data = parser.parse(job_data.raw_jd)
    
    # Create job record
    job = Job(
        user_id=job_data.user_id,
        raw_jd=job_data.raw_jd,
        source_name=job_data.source_name,
        source_url=job_data.source_url,
        title=parsed_data.get("title"),
        company=parsed_data.get("company"),
        location=parsed_data.get("location"),
        remote_policy=parsed_data.get("remote_policy"),
        salary_min=parsed_data.get("salary", {}).get("min"),
        salary_max=parsed_data.get("salary", {}).get("max"),
        salary_currency=parsed_data.get("salary", {}).get("currency"),
        is_processed=True,
        processed_at=datetime.now()
    )
    db.add(job)
    db.flush()  # Get job ID
    
    # Create job skills
    for skill_data in parsed_data.get("skills", []):
        skill = JobSkill(
            job_id=job.id,
            skill_name=skill_data.get("name"),
            skill_category=skill_data.get("category"),
            is_mandatory=skill_data.get("is_mandatory", True),
            is_preferred=skill_data.get("is_preferred", False),
            proficiency_required=skill_data.get("proficiency_required"),
            years_required=skill_data.get("years_required"),
            context=skill_data.get("context")
        )
        db.add(skill)
    
    # Create job responsibilities
    for resp_data in parsed_data.get("responsibilities", []):
        resp = JobResponsibility(
            job_id=job.id,
            description=resp_data,
            category="Technical"  # Default
        )
        db.add(resp)
    
    # Generate Job DNA
    dna_data = dna_generator.generate(parsed_data)
    
    # Create Job DNA record
    job_dna = JobDNA(
        job_id=job.id,
        role_family=dna_data.get("role_family"),
        seniority=dna_data.get("seniority"),
        capabilities=dna_data.get("capabilities"),
        skills=dna_data.get("skills"),
        mandatory_skills=dna_data.get("mandatory_skills"),
        preferred_skills=dna_data.get("preferred_skills"),
        technologies=dna_data.get("technologies"),
        experience_requirements=dna_data.get("experience_requirements"),
        architecture_domains=dna_data.get("architecture_domains"),
        leadership_scope=dna_data.get("leadership_scope"),
        governance_requirements=dna_data.get("governance_requirements"),
        industry=dna_data.get("industry"),
        location=dna_data.get("location"),
        mobility_requirements=dna_data.get("mobility_requirements"),
        education_requirements=dna_data.get("education_requirements"),
        certifications_required=dna_data.get("certifications_required"),
        summary=dna_data.get("summary"),
        keywords=dna_data.get("keywords"),
        confidence_score=dna_data.get("confidence_score"),
        completeness_score=dna_data.get("completeness_score")
    )
    db.add(job_dna)
    
    db.commit()
    db.refresh(job)
    db.refresh(job_dna)
    
    # Return response
    return JobDNAResponse(
        id=job_dna.id,
        job_id=job.id,
        role_family=job_dna.role_family,
        seniority=job_dna.seniority,
        capabilities=job_dna.capabilities,
        skills=job_dna.skills,
        mandatory_skills=job_dna.mandatory_skills,
        preferred_skills=job_dna.preferred_skills,
        technologies=job_dna.technologies,
        experience_requirements=job_dna.experience_requirements,
        architecture_domains=job_dna.architecture_domains,
        leadership_scope=job_dna.leadership_scope,
        governance_requirements=job_dna.governance_requirements,
        industry=job_dna.industry,
        location=job_dna.location,
        mobility_requirements=job_dna.mobility_requirements,
        education_requirements=job_dna.education_requirements,
        certifications_required=job_dna.certifications_required,
        summary=job_dna.summary,
        keywords=job_dna.keywords,
        confidence_score=job_dna.confidence_score,
        completeness_score=job_dna.completeness_score,
        created_at=job_dna.created_at,
        updated_at=job_dna.updated_at
    )


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """List jobs for a user."""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id is required"
        )
    
    jobs = db.query(Job).filter(Job.user_id == user_id).all()
    return jobs


@router.get("/{job_id}/dna", response_model=JobDNAResponse)
async def get_job_dna(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """Get Job DNA for a specific job."""
    job_dna = db.query(JobDNA).filter(JobDNA.job_id == job_id).first()
    if not job_dna:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job DNA not found"
        )
    return job_dna


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a job and its DNA."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    db.delete(job)
    db.commit()
    
    return None
