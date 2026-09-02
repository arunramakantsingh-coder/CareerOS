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


def _profile_for_user(current_user: User, db: Session) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id, CandidateProfile.is_active == True).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found. Please create one.")
    return profile


def _recalculate(profile: CandidateProfile, db: Session) -> None:
    profile.completeness_score = calculate_completeness(profile.id, db)
    db.commit()


# ============================================
# CANDIDATE PROFILE
# ============================================

@router.get("/", response_model=CandidateProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _profile_for_user(current_user, db)


@router.post("/", response_model=CandidateProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(profile_data: CandidateProfileCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already exists")
    profile = CandidateProfile(user_id=current_user.id, full_name=profile_data.full_name, location=profile_data.location, title=profile_data.title, summary=profile_data.summary, linkedin_url=profile_data.linkedin_url, linkedin_username=profile_data.linkedin_username, primary_email=profile_data.primary_email, primary_phone=profile_data.primary_phone, work_preferences=profile_data.work_preferences, years_experience=profile_data.years_experience, industries=profile_data.industries, seniority=profile_data.seniority, completeness_score=0.0, reconciliation_status="pending")
    db.add(profile); db.commit(); db.refresh(profile)
    return profile


@router.put("/", response_model=CandidateProfileResponse)
def update_profile(profile_data: CandidateProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _profile_for_user(current_user, db)
    for key, value in profile_data.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    profile.completeness_score = calculate_completeness(profile.id, db)
    db.commit(); db.refresh(profile)
    return profile


# ============================================
# PROFESSIONAL EXPERIENCE
# ============================================

@router.get("/experiences", response_model=List[ProfessionalExperienceResponse])
def get_experiences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id, CandidateProfile.is_active == True).first()
    if not profile: return []
    return db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == profile.id).order_by(ProfessionalExperience.start_date.desc()).all()


@router.post("/experiences", response_model=ProfessionalExperienceResponse, status_code=status.HTTP_201_CREATED)
def create_experience(experience_data: ProfessionalExperienceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _profile_for_user(current_user, db)
    experience = ProfessionalExperience(candidate_id=profile.id, **experience_data.dict(exclude={"candidate_id"}))
    db.add(experience); db.commit(); db.refresh(experience); _recalculate(profile, db)
    return experience


@router.put("/experiences/{experience_id}", response_model=ProfessionalExperienceResponse)
def update_experience(experience_id: uuid.UUID, experience_data: ProfessionalExperienceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experience = db.query(ProfessionalExperience).filter(ProfessionalExperience.id == experience_id).first()
    if not experience: raise HTTPException(status_code=404, detail="Experience not found")
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == experience.candidate_id, CandidateProfile.user_id == current_user.id).first()
    if not profile: raise HTTPException(status_code=403, detail="Not authorized")
    for key, value in experience_data.dict(exclude_unset=True).items(): setattr(experience, key, value)
    db.commit(); db.refresh(experience); _recalculate(profile, db)
    return experience


@router.delete("/experiences/{experience_id}")
def delete_experience(experience_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experience = db.query(ProfessionalExperience).filter(ProfessionalExperience.id == experience_id).first()
    if not experience: raise HTTPException(status_code=404, detail="Experience not found")
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == experience.candidate_id, CandidateProfile.user_id == current_user.id).first()
    if not profile: raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(experience); db.commit(); _recalculate(profile, db)
    return {"message": "Experience deleted"}


# ============================================
# SKILLS
# ============================================

@router.get("/skills", response_model=List[CandidateSkillResponse])
def get_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id, CandidateProfile.is_active == True).first()
    if not profile: return []
    return db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id).all()


@router.post("/skills", response_model=CandidateSkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(skill_data: CandidateSkillCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _profile_for_user(current_user, db)
    skill = CandidateSkill(candidate_id=profile.id, **skill_data.dict(exclude={"candidate_id"}))
    db.add(skill); db.commit(); db.refresh(skill); _recalculate(profile, db)
    return skill


@router.put("/skills/{skill_id}", response_model=CandidateSkillResponse)
def update_skill(skill_id: uuid.UUID, skill_data: CandidateSkillUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    skill = db.query(CandidateSkill).filter(CandidateSkill.id == skill_id).first()
    if not skill: raise HTTPException(status_code=404, detail="Skill not found")
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == skill.candidate_id, CandidateProfile.user_id == current_user.id).first()
    if not profile: raise HTTPException(status_code=403, detail="Not authorized")
    for key, value in skill_data.dict(exclude_unset=True).items(): setattr(skill, key, value)
    db.commit(); db.refresh(skill); _recalculate(profile, db)
    return skill


@router.delete("/skills/{skill_id}")
def delete_skill(skill_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    skill = db.query(CandidateSkill).filter(CandidateSkill.id == skill_id).first()
    if not skill: raise HTTPException(status_code=404, detail="Skill not found")
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == skill.candidate_id, CandidateProfile.user_id == current_user.id).first()
    if not profile: raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(skill); db.commit(); _recalculate(profile, db)
    return {"message": "Skill deleted"}


# ============================================
# CERTIFICATIONS
# ============================================

@router.get("/certifications", response_model=List[CandidateCertificationResponse])
def get_certifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id, CandidateProfile.is_active == True).first()
    if not profile: return []
    return db.query(CandidateCertification).filter(CandidateCertification.candidate_id == profile.id).all()


@router.post("/certifications", response_model=CandidateCertificationResponse, status_code=status.HTTP_201_CREATED)
def create_certification(cert_data: CandidateCertificationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _profile_for_user(current_user, db)
    cert = CandidateCertification(candidate_id=profile.id, **cert_data.dict(exclude={"candidate_id"}))
    db.add(cert); db.commit(); db.refresh(cert); _recalculate(profile, db)
    return cert


@router.put("/certifications/{certification_id}", response_model=CandidateCertificationResponse)
def update_certification(certification_id: uuid.UUID, cert_data: CandidateCertificationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cert = db.query(CandidateCertification).filter(CandidateCertification.id == certification_id).first()
    if not cert: raise HTTPException(status_code=404, detail="Certification not found")
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == cert.candidate_id, CandidateProfile.user_id == current_user.id).first()
    if not profile: raise HTTPException(status_code=403, detail="Not authorized")
    for key, value in cert_data.dict(exclude_unset=True).items(): setattr(cert, key, value)
    db.commit(); db.refresh(cert); _recalculate(profile, db)
    return cert


@router.delete("/certifications/{certification_id}")
def delete_certification(certification_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cert = db.query(CandidateCertification).filter(CandidateCertification.id == certification_id).first()
    if not cert: raise HTTPException(status_code=404, detail="Certification not found")
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == cert.candidate_id, CandidateProfile.user_id == current_user.id).first()
    if not profile: raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(cert); db.commit(); _recalculate(profile, db)
    return {"message": "Certification deleted"}


# ============================================
# EDUCATION
# ============================================

@router.get("/educations", response_model=List[CandidateEducationResponse])
def get_educations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id, CandidateProfile.is_active == True).first()
    if not profile: return []
    return db.query(CandidateEducation).filter(CandidateEducation.candidate_id == profile.id).all()


@router.post("/educations", response_model=CandidateEducationResponse, status_code=status.HTTP_201_CREATED)
def create_education(edu_data: CandidateEducationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _profile_for_user(current_user, db)
    edu = CandidateEducation(candidate_id=profile.id, **edu_data.dict(exclude={"candidate_id"}))
    db.add(edu); db.commit(); db.refresh(edu); _recalculate(profile, db)
    return edu


@router.put("/educations/{education_id}", response_model=CandidateEducationResponse)
def update_education(education_id: uuid.UUID, edu_data: CandidateEducationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    edu = db.query(CandidateEducation).filter(CandidateEducation.id == education_id).first()
    if not edu: raise HTTPException(status_code=404, detail="Education not found")
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == edu.candidate_id, CandidateProfile.user_id == current_user.id).first()
    if not profile: raise HTTPException(status_code=403, detail="Not authorized")
    for key, value in edu_data.dict(exclude_unset=True).items(): setattr(edu, key, value)
    db.commit(); db.refresh(edu); _recalculate(profile, db)
    return edu


@router.delete("/educations/{education_id}")
def delete_education(education_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    edu = db.query(CandidateEducation).filter(CandidateEducation.id == education_id).first()
    if not edu: raise HTTPException(status_code=404, detail="Education not found")
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == edu.candidate_id, CandidateProfile.user_id == current_user.id).first()
    if not profile: raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(edu); db.commit(); _recalculate(profile, db)
    return {"message": "Education deleted"}


# ============================================
# PROFILE COMPLETENESS
# ============================================

def calculate_completeness(profile_id: uuid.UUID, db: Session) -> float:
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == profile_id).first()
    if not profile: return 0.0
    sections = {
        "Personal Information": {"fields": ["full_name", "location", "title", "summary"], "weight": 20, "filled": 0},
        "Contact Information": {"fields": ["primary_email", "primary_phone", "linkedin_url"], "weight": 15, "filled": 0},
        "Professional Experience": {"weight": 25, "filled": 0}, "Skills": {"weight": 15, "filled": 0},
        "Certifications": {"weight": 10, "filled": 0}, "Education": {"weight": 15, "filled": 0}
    }
    for field in sections["Personal Information"]["fields"]:
        if getattr(profile, field, None): sections["Personal Information"]["filled"] += 1
    sections["Personal Information"]["filled"] = sections["Personal Information"]["filled"] / 4 * 100
    for field in sections["Contact Information"]["fields"]:
        if getattr(profile, field, None): sections["Contact Information"]["filled"] += 1
    sections["Contact Information"]["filled"] = sections["Contact Information"]["filled"] / 3 * 100
    sections["Professional Experience"]["filled"] = min(db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == profile_id).count() * 20, 100)
    sections["Skills"]["filled"] = min(db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile_id).count() * 10, 100)
    sections["Certifications"]["filled"] = min(db.query(CandidateCertification).filter(CandidateCertification.candidate_id == profile_id).count() * 20, 100)
    sections["Education"]["filled"] = min(db.query(CandidateEducation).filter(CandidateEducation.candidate_id == profile_id).count() * 25, 100)
    return round(sum((data["filled"] / 100) * data["weight"] for data in sections.values()), 1)


@router.get("/completeness", response_model=ProfileCompletenessResponse)
def get_completeness(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _profile_for_user(current_user, db); score = calculate_completeness(profile.id, db)
    counts = {
        "Professional Experience": db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == profile.id).count(),
        "Skills": db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id).count(),
        "Certifications": db.query(CandidateCertification).filter(CandidateCertification.candidate_id == profile.id).count(),
        "Education": db.query(CandidateEducation).filter(CandidateEducation.candidate_id == profile.id).count(),
    }
    breakdown = {"Personal Information": 100 if any([profile.full_name, profile.location, profile.title, profile.summary]) else 0, "Contact Information": 100 if any([profile.primary_email, profile.primary_phone, profile.linkedin_url]) else 0, **{key: 100 if value else 0 for key, value in counts.items()}}
    missing_items = []
    if not profile.full_name: missing_items.append("Full Name")
    if not profile.primary_phone: missing_items.append("Primary Phone")
    if not profile.title: missing_items.append("Professional Title")
    if not counts["Professional Experience"]: missing_items.append("Professional Experience")
    if not counts["Skills"]: missing_items.append("Skills")
    if not counts["Education"]: missing_items.append("Education")
    suggestions = [f"Add at least {max(0, 3-counts['Professional Experience'])} more experience entries" if counts["Professional Experience"] < 3 else "Experience timeline looks good"]
    if counts["Skills"] < 5: suggestions.append("Add or confirm at least 5 core skills")
    if not profile.primary_phone: suggestions.append("Add your primary phone number")
    return ProfileCompletenessResponse(overall_score=score, breakdown=breakdown, missing_items=missing_items, suggestions=suggestions)
