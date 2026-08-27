from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
import json
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.professional_experience import ProfessionalExperience
from app.models.candidate_skill import CandidateSkill
from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation
from app.models.document import Document
from app.schemas.candidate import (
    CandidateProfileCreate, CandidateProfileUpdate, CandidateProfileResponse,
    ProfessionalExperienceCreate, ProfessionalExperienceUpdate, ProfessionalExperienceResponse,
    CandidateSkillCreate, CandidateSkillUpdate, CandidateSkillResponse,
    CandidateCertificationCreate, CandidateCertificationUpdate, CandidateCertificationResponse,
    CandidateEducationCreate, CandidateEducationUpdate, CandidateEducationResponse,
    DocumentResponse, ProfileCompletenessResponse
)

router = APIRouter(prefix="/profile", tags=["profile"])


# ============================================
# CANDIDATE PROFILE
# ============================================

@router.get("/", response_model=CandidateProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's candidate profile."""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create one."
        )
    
    return profile


@router.post("/", response_model=CandidateProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_data: CandidateProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a candidate profile."""
    
    # Check if profile already exists
    existing = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists"
        )
    
    profile = CandidateProfile(
        user_id=current_user.id,
        full_name=profile_data.full_name,
        location=profile_data.location,
        title=profile_data.title,
        summary=profile_data.summary,
        linkedin_url=profile_data.linkedin_url,
        linkedin_username=profile_data.linkedin_username,
        primary_email=profile_data.primary_email,
        primary_phone=profile_data.primary_phone,
        work_preferences=profile_data.work_preferences,
        years_experience=profile_data.years_experience,
        industries=profile_data.industries,
        seniority=profile_data.seniority,
        completeness_score=0.0,
        reconciliation_status="pending"
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile


@router.put("/", response_model=CandidateProfileResponse)
def update_profile(
    profile_data: CandidateProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the current user's candidate profile."""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    for key, value in profile_data.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    
    # Recalculate completeness
    profile.completeness_score = calculate_completeness(profile.id, db)
    
    db.commit()
    db.refresh(profile)
    
    return profile


# ============================================
# PROFESSIONAL EXPERIENCE
# ============================================

@router.get("/experiences", response_model=List[ProfessionalExperienceResponse])
def get_experiences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all professional experiences for the current user."""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        return []
    
    experiences = db.query(ProfessionalExperience).filter(
        ProfessionalExperience.candidate_id == profile.id
    ).order_by(ProfessionalExperience.start_date.desc()).all()
    
    return experiences


@router.post("/experiences", response_model=ProfessionalExperienceResponse, status_code=status.HTTP_201_CREATED)
def create_experience(
    experience_data: ProfessionalExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a professional experience."""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    experience = ProfessionalExperience(
        candidate_id=profile.id,
        **experience_data.dict(exclude={"candidate_id"})
    )
    db.add(experience)
    db.commit()
    db.refresh(experience)
    
    # Recalculate completeness
    profile.completeness_score = calculate_completeness(profile.id, db)
    db.commit()
    
    return experience


@router.put("/experiences/{experience_id}", response_model=ProfessionalExperienceResponse)
def update_experience(
    experience_id: uuid.UUID,
    experience_data: ProfessionalExperienceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a professional experience."""
    experience = db.query(ProfessionalExperience).filter(
        ProfessionalExperience.id == experience_id
    ).first()
    
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
    
    # Verify ownership
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.id == experience.candidate_id,
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    for key, value in experience_data.dict(exclude_unset=True).items():
        setattr(experience, key, value)
    
    db.commit()
    db.refresh(experience)
    
    # Recalculate completeness
    profile.completeness_score = calculate_completeness(profile.id, db)
    db.commit()
    
    return experience


@router.delete("/experiences/{experience_id}")
def delete_experience(
    experience_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a professional experience."""
    experience = db.query(ProfessionalExperience).filter(
        ProfessionalExperience.id == experience_id
    ).first()
    
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
    
    # Verify ownership
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.id == experience.candidate_id,
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    db.delete(experience)
    db.commit()
    
    # Recalculate completeness
    profile.completeness_score = calculate_completeness(profile.id, db)
    db.commit()
    
    return {"message": "Experience deleted"}


# ============================================
# SKILLS
# ============================================

@router.get("/skills", response_model=List[CandidateSkillResponse])
def get_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all skills for the current user."""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        return []
    
    skills = db.query(CandidateSkill).filter(
        CandidateSkill.candidate_id == profile.id
    ).all()
    
    return skills


@router.post("/skills", response_model=CandidateSkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_data: CandidateSkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a skill."""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    skill = CandidateSkill(
        candidate_id=profile.id,
        **skill_data.dict(exclude={"candidate_id"})
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    
    # Recalculate completeness
    profile.completeness_score = calculate_completeness(profile.id, db)
    db.commit()
    
    return skill


@router.delete("/skills/{skill_id}")
def delete_skill(
    skill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a skill."""
    skill = db.query(CandidateSkill).filter(
        CandidateSkill.id == skill_id
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    # Verify ownership
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.id == skill.candidate_id,
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    db.delete(skill)
    db.commit()
    
    # Recalculate completeness
    profile.completeness_score = calculate_completeness(profile.id, db)
    db.commit()
    
    return {"message": "Skill deleted"}


# ============================================
# CERTIFICATIONS
# ============================================

@router.get("/certifications", response_model=List[CandidateCertificationResponse])
def get_certifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all certifications for the current user."""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        return []
    
    certifications = db.query(CandidateCertification).filter(
        CandidateCertification.candidate_id == profile.id
    ).all()
    
    return certifications


@router.post("/certifications", response_model=CandidateCertificationResponse, status_code=status.HTTP_201_CREATED)
def create_certification(
    cert_data: CandidateCertificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a certification."""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    cert = CandidateCertification(
        candidate_id=profile.id,
        **cert_data.dict(exclude={"candidate_id"})
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    
    # Recalculate completeness
    profile.completeness_score = calculate_completeness(profile.id, db)
    db.commit()
    
    return cert


# ============================================
# EDUCATION
# ============================================

@router.get("/educations", response_model=List[CandidateEducationResponse])
def get_educations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all education entries for the current user."""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        return []
    
    educations = db.query(CandidateEducation).filter(
        CandidateEducation.candidate_id == profile.id
    ).all()
    
    return educations


@router.post("/educations", response_model=CandidateEducationResponse, status_code=status.HTTP_201_CREATED)
def create_education(
    edu_data: CandidateEducationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an education entry."""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    edu = CandidateEducation(
        candidate_id=profile.id,
        **edu_data.dict(exclude={"candidate_id"})
    )
    db.add(edu)
    db.commit()
    db.refresh(edu)
    
    # Recalculate completeness
    profile.completeness_score = calculate_completeness(profile.id, db)
    db.commit()
    
    return edu


# ============================================
# PROFILE COMPLETENESS
# ============================================

def calculate_completeness(profile_id: uuid.UUID, db: Session) -> float:
    """Calculate profile completeness score."""
    # Get profile
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.id == profile_id
    ).first()
    
    if not profile:
        return 0.0
    
    # Define sections and weights
    sections = {
        "Personal Information": {
            "fields": ["full_name", "location", "title", "summary"],
            "weight": 20,
            "filled": 0
        },
        "Contact Information": {
            "fields": ["primary_email", "primary_phone", "linkedin_url"],
            "weight": 15,
            "filled": 0
        },
        "Professional Experience": {
            "weight": 25,
            "filled": 0
        },
        "Skills": {
            "weight": 15,
            "filled": 0
        },
        "Certifications": {
            "weight": 10,
            "filled": 0
        },
        "Education": {
            "weight": 15,
            "filled": 0
        }
    }
    
    # Check Personal Information
    for field in sections["Personal Information"]["fields"]:
        if getattr(profile, field, None):
            sections["Personal Information"]["filled"] += 1
    sections["Personal Information"]["filled"] = (sections["Personal Information"]["filled"] / len(sections["Personal Information"]["fields"])) * 100
    
    # Check Contact Information
    for field in sections["Contact Information"]["fields"]:
        if getattr(profile, field, None):
            sections["Contact Information"]["filled"] += 1
    sections["Contact Information"]["filled"] = (sections["Contact Information"]["filled"] / len(sections["Contact Information"]["fields"])) * 100
    
    # Check Professional Experience
    experiences = db.query(ProfessionalExperience).filter(
        ProfessionalExperience.candidate_id == profile_id
    ).count()
    sections["Professional Experience"]["filled"] = min(experiences * 20, 100)  # 5 experiences = 100%
    
    # Check Skills
    skills = db.query(CandidateSkill).filter(
        CandidateSkill.candidate_id == profile_id
    ).count()
    sections["Skills"]["filled"] = min(skills * 10, 100)  # 10 skills = 100%
    
    # Check Certifications
    certs = db.query(CandidateCertification).filter(
        CandidateCertification.candidate_id == profile_id
    ).count()
    sections["Certifications"]["filled"] = min(certs * 20, 100)  # 5 certifications = 100%
    
    # Check Education
    educations = db.query(CandidateEducation).filter(
        CandidateEducation.candidate_id == profile_id
    ).count()
    sections["Education"]["filled"] = min(educations * 25, 100)  # 4 educations = 100%
    
    # Calculate overall score
    total_score = 0
    for section, data in sections.items():
        total_score += (data["filled"] / 100) * data["weight"]
    
    return round(total_score, 1)


@router.get("/completeness", response_model=ProfileCompletenessResponse)
def get_completeness(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get profile completeness score and breakdown."""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Calculate completeness
    score = calculate_completeness(profile.id, db)
    
    # Build breakdown
    breakdown = {
        "Personal Information": 0,
        "Contact Information": 0,
        "Professional Experience": 0,
        "Skills": 0,
        "Certifications": 0,
        "Education": 0
    }
    
    # Calculate section scores
    if profile.full_name or profile.location or profile.title or profile.summary:
        breakdown["Personal Information"] = 100
    if profile.primary_email or profile.primary_phone or profile.linkedin_url:
        breakdown["Contact Information"] = 100
    if db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == profile.id).count() > 0:
        breakdown["Professional Experience"] = 100
    if db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id).count() > 0:
        breakdown["Skills"] = 100
    if db.query(CandidateCertification).filter(CandidateCertification.candidate_id == profile.id).count() > 0:
        breakdown["Certifications"] = 100
    if db.query(CandidateEducation).filter(CandidateEducation.candidate_id == profile.id).count() > 0:
        breakdown["Education"] = 100
    
    # Identify missing items
    missing_items = []
    if not profile.full_name:
        missing_items.append("Full Name")
    if not profile.primary_email:
        missing_items.append("Primary Email")
    if not profile.primary_phone:
        missing_items.append("Primary Phone")
    if db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == profile.id).count() == 0:
        missing_items.append("Professional Experience")
    if db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id).count() == 0:
        missing_items.append("Skills")
    
    suggestions = []
    if not profile.full_name:
        suggestions.append("Add your full name")
    if not profile.primary_email:
        suggestions.append("Add your primary email")
    if not profile.primary_phone:
        suggestions.append("Add your primary phone")
    if db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == profile.id).count() < 3:
        suggestions.append("Add more professional experiences")
    if db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id).count() < 5:
        suggestions.append("Add more skills")
    
    return ProfileCompletenessResponse(
        overall_score=score,
        breakdown=breakdown,
        missing_items=missing_items,
        suggestions=suggestions
    )
