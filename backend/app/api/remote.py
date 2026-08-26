from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.job import Job
from app.models.job_dna import JobDNA
from app.models.remote_eligibility import RemoteEligibility
from app.schemas.remote import RemoteEvaluationRequest, RemoteEvaluationResponse, RemoteClassification
from app.utils.remote_engine import RemoteEngine

router = APIRouter(prefix="/remote", tags=["remote"])
remote_engine = RemoteEngine()


@router.post("/evaluate", response_model=RemoteEvaluationResponse)
async def evaluate_remote(
    request: RemoteEvaluationRequest,
    db: Session = Depends(get_db)
):
    """Evaluate remote eligibility for a job."""
    
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify job exists
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get job DNA
    job_dna = db.query(JobDNA).filter(JobDNA.job_id == request.job_id).first()
    
    # Prepare user data
    user_data = {
        "candidate_location": user.candidate_location,
        "candidate_timezone": user.candidate_timezone,
        "candidate_authorization": user.candidate_authorization,
    }
    
    # Prepare job data
    job_data = {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "remote_policy": job.remote_policy,
        "job_dna": {
            "location": job_dna.location if job_dna else {},
            "mobility_requirements": job_dna.mobility_requirements if job_dna else {},
            "employment_model": job_dna.employment_model if job_dna else {},
            "technologies": job_dna.technologies if job_dna else [],
        } if job_dna else {}
    }
    
    # Evaluate remote eligibility
    result = remote_engine.evaluate(user_data, job_data)
    
    # Save evaluation
    evaluation = RemoteEligibility(
        user_id=request.user_id,
        job_id=request.job_id,
        remote_classification=result["remote_classification"],
        overall_remote_score=result["overall_remote_score"],
        timezone_score=result["timezone_score"],
        authorization_score=result["authorization_score"],
        sponsorship_score=result["sponsorship_score"],
        contractor_score=result["contractor_score"],
        relocation_score=result["relocation_score"],
        remote_analysis=result.get("remote_analysis"),
        restrictions=result.get("restrictions"),
        requirements=result.get("requirements"),
        is_remote_eligible=result["is_remote_eligible"],
        is_timezone_compatible=result["is_timezone_compatible"],
        has_work_authorization=result["has_work_authorization"],
        requires_sponsorship=result["requires_sponsorship"],
        requires_relocation=result["requires_relocation"],
        allows_contractor=result["allows_contractor"],
        allows_eor=result["allows_eor"],
        candidate_location=user.candidate_location,
        candidate_timezone=user.candidate_timezone,
        candidate_authorization=user.candidate_authorization,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    return RemoteEvaluationResponse(
        id=evaluation.id,
        user_id=evaluation.user_id,
        job_id=evaluation.job_id,
        remote_classification=evaluation.remote_classification,
        overall_remote_score=evaluation.overall_remote_score,
        timezone_score=evaluation.timezone_score,
        authorization_score=evaluation.authorization_score,
        sponsorship_score=evaluation.sponsorship_score,
        contractor_score=evaluation.contractor_score,
        relocation_score=evaluation.relocation_score,
        is_remote_eligible=evaluation.is_remote_eligible,
        is_timezone_compatible=evaluation.is_timezone_compatible,
        has_work_authorization=evaluation.has_work_authorization,
        requires_sponsorship=evaluation.requires_sponsorship,
        requires_relocation=evaluation.requires_relocation,
        allows_contractor=evaluation.allows_contractor,
        allows_eor=evaluation.allows_eor,
        restrictions=evaluation.restrictions,
        requirements=evaluation.requirements,
        remote_analysis=evaluation.remote_analysis,
        created_at=evaluation.created_at,
        updated_at=evaluation.updated_at
    )


@router.get("/evaluations", response_model=List[RemoteEvaluationResponse])
async def list_evaluations(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """List remote evaluations for a user."""
    evaluations = db.query(RemoteEligibility).filter(
        RemoteEligibility.user_id == user_id
    ).order_by(RemoteEligibility.created_at.desc()).all()
    
    return evaluations


@router.get("/evaluations/{evaluation_id}", response_model=RemoteEvaluationResponse)
async def get_evaluation(
    evaluation_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific remote evaluation."""
    evaluation = db.query(RemoteEligibility).filter(
        RemoteEligibility.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remote evaluation not found"
        )
    
    return evaluation


@router.put("/user/location")
async def update_user_location(
    user_id: UUID,
    location: str,
    timezone: Optional[str] = None,
    authorization: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Update user's location for remote eligibility."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.candidate_location = location
    if timezone:
        user.candidate_timezone = timezone
    if authorization:
        user.candidate_authorization = authorization
    
    db.commit()
    
    return {"message": "User location updated successfully"}


@router.post("/classify/{job_id}", response_model=RemoteClassification)
async def classify_job_remote(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """Classify a job's remote scope."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job_dna = db.query(JobDNA).filter(JobDNA.job_id == job_id).first()
    
    job_data = {
        "location": job.location,
        "remote_policy": job.remote_policy,
        "job_dna": {
            "location": job_dna.location if job_dna else {},
            "mobility_requirements": job_dna.mobility_requirements if job_dna else {},
        } if job_dna else {}
    }
    
    classification = remote_engine._classify_job(job_data)
    
    return RemoteClassification(
        job_id=job_id,
        classification=classification,
        job_title=job.title,
        company=job.company
    )
