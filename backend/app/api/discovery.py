from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.persona import Persona
from app.models.job import Job
from app.models.job_dna import JobDNA
from app.models.job_discovery import JobDiscovery
from app.models.career_profile import CareerProfile
from app.schemas.discovery import DiscoveryRequest, DiscoveryResponse, DiscoveryResult
from app.utils.semantic_discovery import SemanticDiscoveryEngine

router = APIRouter(prefix="/discover", tags=["discovery"])
discovery_engine = SemanticDiscoveryEngine()


@router.post("/", response_model=DiscoveryResponse)
async def discover_jobs(
    request: DiscoveryRequest,
    db: Session = Depends(get_db)
):
    """Discover jobs semantically matched to the career profile."""
    
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get persona
    persona = db.query(Persona).filter(Persona.id == request.persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    # Get career profile
    career_profile_data = {}
    if persona.career_profile_id:
        profile = db.query(CareerProfile).filter(
            CareerProfile.id == persona.career_profile_id
        ).first()
        if profile:
            career_profile_data = {
                "skills": profile.skills if profile.skills else [],
                "employments": profile.employments if profile.employments else [],
                "projects": profile.projects if profile.projects else [],
                "certifications": profile.certifications if profile.certifications else [],
                "educations": profile.educations if profile.educations else [],
                "achievements": profile.achievements if profile.achievements else [],
            }
    
    # Get jobs to discover
    if request.job_ids:
        jobs = db.query(Job).filter(Job.id.in_(request.job_ids), Job.is_active == True).all()
    else:
        jobs = db.query(Job).filter(Job.is_active == True).limit(100).all()
    
    if not jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No jobs found for discovery"
        )
    
    # Prepare jobs with DNA
    jobs_with_dna = []
    for job in jobs:
        job_dna = db.query(JobDNA).filter(JobDNA.job_id == job.id).first()
        if job_dna:
            job_dict = {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "job_dna": {
                    "skills": job_dna.skills or {},
                    "capabilities": job_dna.capabilities or {},
                    "responsibilities": job_dna.responsibilities or [],
                    "seniority": job_dna.seniority,
                    "industry": job_dna.industry,
                    "location": job_dna.location or {},
                }
            }
            jobs_with_dna.append(job_dict)
    
    # Persona data for discovery
    persona_data = {
        "target_titles": persona.target_titles or [],
        "target_industries": persona.target_industries or [],
        "target_locations": persona.target_locations or [],
        "preferred_seniority": persona.preferred_seniority,
        "remote_preference": persona.remote_preference,
    }
    
    # Run discovery
    results = discovery_engine.discover(
        career_profile_data,
        persona_data,
        jobs_with_dna
    )
    
    # Save discovery results
    discovery_results = []
    for result in results:
        # Check if discovery already exists
        existing = db.query(JobDiscovery).filter(
            JobDiscovery.user_id == request.user_id,
            JobDiscovery.job_id == result["job_id"]
        ).first()
        
        if existing:
            # Update existing
            existing.overall_score = result["overall_score"]
            existing.title_match = result["title_match"]
            existing.capability_match = result["capability_match"]
            existing.skill_match = result["skill_match"]
            existing.responsibility_match = result["responsibility_match"]
            existing.career_match = result["career_match"]
            existing.capability_details = result["capability_details"]
            existing.skill_details = result["skill_details"]
            existing.responsibility_details = result["responsibility_details"]
            existing.career_details = result["career_details"]
            existing.discovery_rank = result["discovery_rank"]
            existing.discovery_confidence = result["discovery_confidence"]
            existing.matched_capabilities = result["matched_capabilities"]
            existing.missing_capabilities = result["missing_capabilities"]
            db.commit()
            db.refresh(existing)
            discovery_results.append(existing)
        else:
            # Create new
            discovery = JobDiscovery(
                user_id=request.user_id,
                job_id=result["job_id"],
                overall_score=result["overall_score"],
                title_match=result["title_match"],
                capability_match=result["capability_match"],
                skill_match=result["skill_match"],
                responsibility_match=result["responsibility_match"],
                career_match=result["career_match"],
                capability_details=result["capability_details"],
                skill_details=result["skill_details"],
                responsibility_details=result["responsibility_details"],
                career_details=result["career_details"],
                discovery_rank=result["discovery_rank"],
                discovery_confidence=result["discovery_confidence"],
                matched_capabilities=result["matched_capabilities"],
                missing_capabilities=result["missing_capabilities"],
            )
            db.add(discovery)
            db.commit()
            db.refresh(discovery)
            discovery_results.append(discovery)
    
    return DiscoveryResponse(
        user_id=request.user_id,
        persona_id=request.persona_id,
        total_discovered=len(results),
        results=results
    )


@router.get("/saved", response_model=List[DiscoveryResult])
async def get_saved_discoveries(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get saved discoveries for a user."""
    discoveries = db.query(JobDiscovery).filter(
        JobDiscovery.user_id == user_id,
        JobDiscovery.is_saved == True
    ).order_by(JobDiscovery.overall_score.desc()).all()
    
    results = []
    for d in discoveries:
        job = db.query(Job).filter(Job.id == d.job_id).first()
        results.append({
            "job_id": str(d.job_id),
            "job_title": job.title if job else "Unknown",
            "company": job.company if job else "Unknown",
            "location": job.location if job else "Unknown",
            "overall_score": d.overall_score,
            "title_match": d.title_match,
            "capability_match": d.capability_match,
            "skill_match": d.skill_match,
            "responsibility_match": d.responsibility_match,
            "career_match": d.career_match,
            "capability_details": d.capability_details,
            "skill_details": d.skill_details,
            "responsibility_details": d.responsibility_details,
            "career_details": d.career_details,
            "discovery_rank": d.discovery_rank,
            "discovery_confidence": d.discovery_confidence,
            "matched_capabilities": d.matched_capabilities,
            "missing_capabilities": d.missing_capabilities,
        })
    
    return results


@router.post("/{discovery_id}/save")
async def save_discovery(
    discovery_id: UUID,
    db: Session = Depends(get_db)
):
    """Save a discovery for later."""
    discovery = db.query(JobDiscovery).filter(JobDiscovery.id == discovery_id).first()
    if not discovery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discovery not found"
        )
    
    discovery.is_saved = True
    db.commit()
    
    return {"message": "Discovery saved successfully"}


@router.post("/{discovery_id}/view")
async def view_discovery(
    discovery_id: UUID,
    db: Session = Depends(get_db)
):
    """Mark a discovery as viewed."""
    discovery = db.query(JobDiscovery).filter(JobDiscovery.id == discovery_id).first()
    if not discovery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discovery not found"
        )
    
    discovery.is_viewed = True
    db.commit()
    
    return {"message": "Discovery marked as viewed"}


@router.get("/{discovery_id}", response_model=DiscoveryResult)
async def get_discovery(
    discovery_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific discovery."""
    discovery = db.query(JobDiscovery).filter(JobDiscovery.id == discovery_id).first()
    if not discovery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discovery not found"
        )
    
    job = db.query(Job).filter(Job.id == discovery.job_id).first()
    
    return {
        "job_id": str(discovery.job_id),
        "job_title": job.title if job else "Unknown",
        "company": job.company if job else "Unknown",
        "location": job.location if job else "Unknown",
        "overall_score": discovery.overall_score,
        "title_match": discovery.title_match,
        "capability_match": discovery.capability_match,
        "skill_match": discovery.skill_match,
        "responsibility_match": discovery.responsibility_match,
        "career_match": discovery.career_match,
        "capability_details": discovery.capability_details,
        "skill_details": discovery.skill_details,
        "responsibility_details": discovery.responsibility_details,
        "career_details": discovery.career_details,
        "discovery_rank": discovery.discovery_rank,
        "discovery_confidence": discovery.discovery_confidence,
        "matched_capabilities": discovery.matched_capabilities,
        "missing_capabilities": discovery.missing_capabilities,
    }
