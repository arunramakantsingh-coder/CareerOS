from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.persona import Persona
from app.models.job import Job
from app.models.job_dna import JobDNA
from app.models.match import Match
from app.models.match_dimension import MatchDimension
from app.models.match_recommendation import MatchRecommendation
from app.schemas.match import MatchRequest, MatchResponse, MatchDimensionResponse, MatchRecommendationResponse
from app.utils.match_engine import MatchEngine

router = APIRouter(prefix="/matches", tags=["matches"])
match_engine = MatchEngine()


@router.post("/", response_model=MatchResponse)
async def create_match(
    match_request: MatchRequest,
    db: Session = Depends(get_db)
):
    """Run a career-to-job match."""
    
    # Verify user exists
    user = db.query(User).filter(User.id == match_request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify persona exists
    persona = db.query(Persona).filter(Persona.id == match_request.persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    # Verify job exists and has DNA
    job = db.query(Job).filter(Job.id == match_request.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job_dna = db.query(JobDNA).filter(JobDNA.job_id == match_request.job_id).first()
    if not job_dna:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job DNA not found. Please analyze the job first."
        )
    
    # Get career profile data
    career_profile = {}
    if persona.career_profile_id:
        from app.models.career_profile import CareerProfile
        profile = db.query(CareerProfile).filter(
            CareerProfile.id == persona.career_profile_id
        ).first()
        if profile:
            career_profile = {
                "skills": {skill.name: {"category": skill.category} for skill in profile.skills},
                "employments": [{"start_date": e.start_date, "end_date": e.end_date} for e in profile.employments],
                "technologies": [{"name": t.name} for t in profile.technologies],
                "certifications": [{"name": c.name} for c in profile.certifications],
                "leadership": {},  # Placeholder
                "industries": profile.industries or [],
                "seniority": profile.seniority,
                "years_experience": profile.years_experience,
            }
    
    # Prepare persona data
    persona_data = {
        "target_locations": persona.target_locations or [],
        "remote_preference": persona.remote_preference,
        "salary_preferences": persona.salary_preferences or {},
        "skill_weights": persona.skill_weights or {},
    }
    
    # Prepare job DNA data
    job_dna_data = {
        "skills": job_dna.skills or {},
        "mandatory_skills": job_dna.mandatory_skills or {},
        "preferred_skills": job_dna.preferred_skills or {},
        "experience_requirements": job_dna.experience_requirements or {},
        "architecture_domains": job_dna.architecture_domains or [],
        "leadership_scope": job_dna.leadership_scope or {},
        "governance_requirements": job_dna.governance_requirements or {},
        "industry": job_dna.industry,
        "seniority": job_dna.seniority,
        "location": job_dna.location or {},
        "certifications_required": job_dna.certifications_required or {},
        "responsibilities": [],  # Placeholder - would come from JobResponsibility model
    }
    
    # Run the match engine
    match_result = match_engine.match(career_profile, persona_data, job_dna_data)
    
    # Create match record
    match = Match(
        user_id=match_request.user_id,
        job_id=match_request.job_id,
        persona_id=match_request.persona_id,
        overall_score=match_result["overall_score"],
        dimension_scores=match_result["dimension_scores"],
        status=match_result["status"],
        summary=match_result["summary"],
        recommendation=match_result["recommendation"],
        matched_skills=match_result["matched_skills"],
        partial_skills=match_result["partial_skills"],
        missing_skills=match_result["missing_skills"],
        hard_failures=match_result["hard_failures"],
        gaps=match_result["gaps"],
        risks=match_result["risks"],
    )
    db.add(match)
    db.flush()
    
    # Create dimension records
    for dimension_name, score in match_result["dimension_scores"].items():
        details = match_result["dimension_details"].get(dimension_name, {})
        dimension = MatchDimension(
            match_id=match.id,
            name=dimension_name,
            score=score,
            weight=match_engine.dimension_weights.get(dimension_name, 0.1),
            matched_items=details.get("matched"),
            partial_items=details.get("partial"),
            missing_items=details.get("missing"),
            explanation=details.get("explanation"),
        )
        db.add(dimension)
    
    db.commit()
    db.refresh(match)
    
    # Return response
    return MatchResponse(
        id=match.id,
        user_id=match.user_id,
        job_id=match.job_id,
        persona_id=match.persona_id,
        overall_score=match.overall_score,
        dimension_scores=match.dimension_scores,
        status=match.status,
        summary=match.summary,
        recommendation=match.recommendation,
        matched_skills=match.matched_skills,
        partial_skills=match.partial_skills,
        missing_skills=match.missing_skills,
        hard_failures=match.hard_failures,
        gaps=match.gaps,
        risks=match.risks,
        created_at=match.created_at,
        updated_at=match.updated_at,
    )


@router.get("/", response_model=List[MatchResponse])
async def list_matches(
    user_id: Optional[UUID] = None,
    job_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """List matches for a user or job."""
    query = db.query(Match)
    
    if user_id:
        query = query.filter(Match.user_id == user_id)
    if job_id:
        query = query.filter(Match.job_id == job_id)
    
    matches = query.all()
    return matches


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific match."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    return match


@router.get("/{match_id}/dimensions", response_model=List[MatchDimensionResponse])
async def get_match_dimensions(
    match_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all dimensions for a match."""
    dimensions = db.query(MatchDimension).filter(MatchDimension.match_id == match_id).all()
    return dimensions


@router.get("/{match_id}/recommendations", response_model=List[MatchRecommendationResponse])
async def get_match_recommendations(
    match_id: UUID,
    db: Session = Depends(get_db)
):
    """Get recommendations for a match."""
    recommendations = db.query(MatchRecommendation).filter(MatchRecommendation.match_id == match_id).all()
    return recommendations


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(
    match_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a match."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    db.delete(match)
    db.commit()
    
    return None
