from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.country import Country
from app.models.visa import Visa
from app.models.migration_rule import MigrationRule
from app.models.occupation_mapping import OccupationMapping
from app.models.migration_pathway import MigrationPathway
from app.models.migration_profile import MigrationProfile
from app.schemas.migration import (
    MigrationProfileCreate, MigrationProfileUpdate, MigrationProfileResponse,
    CountryResponse, VisaResponse, MigrationRuleResponse,
    EligibilityRequest, EligibilityResponse, PathwayResponse
)
from app.utils.migration_engine import MigrationEngine

router = APIRouter(prefix="/migration", tags=["migration"])
migration_engine = MigrationEngine()


# ============================================
# COUNTRY ENDPOINTS
# ============================================

@router.get("/countries", response_model=List[CountryResponse])
async def list_countries(
    db: Session = Depends(get_db)
):
    """List all countries with migration data."""
    countries = db.query(Country).filter(Country.is_active == True).all()
    return countries


@router.get("/countries/{country_code}", response_model=CountryResponse)
async def get_country(
    country_code: str,
    db: Session = Depends(get_db)
):
    """Get a specific country."""
    country = db.query(Country).filter(Country.code == country_code).first()
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    return country


@router.get("/countries/{country_code}/visas", response_model=List[VisaResponse])
async def get_country_visas(
    country_code: str,
    db: Session = Depends(get_db)
):
    """Get all visas for a country."""
    country = db.query(Country).filter(Country.code == country_code).first()
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    
    visas = db.query(Visa).filter(
        Visa.country_id == country.id,
        Visa.is_active == True
    ).all()
    return visas


@router.get("/countries/{country_code}/rules", response_model=List[MigrationRuleResponse])
async def get_country_rules(
    country_code: str,
    visa_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get migration rules for a country (optionally filtered by visa)."""
    country = db.query(Country).filter(Country.code == country_code).first()
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    
    query = db.query(MigrationRule).join(Visa).filter(
        Visa.country_id == country.id,
        MigrationRule.is_current == True
    )
    
    if visa_code:
        query = query.filter(Visa.code == visa_code)
    
    rules = query.all()
    return rules


@router.get("/countries/{country_code}/pathways", response_model=List[PathwayResponse])
async def get_country_pathways(
    country_code: str,
    db: Session = Depends(get_db)
):
    """Get migration pathways for a country."""
    country = db.query(Country).filter(Country.code == country_code).first()
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    
    pathways = db.query(MigrationPathway).join(Visa).filter(
        Visa.country_id == country.id,
        MigrationPathway.is_active == True
    ).all()
    return pathways


# ============================================
# MIGRATION PROFILE ENDPOINTS
# ============================================

@router.post("/profiles", response_model=MigrationProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_migration_profile(
    profile_data: MigrationProfileCreate,
    db: Session = Depends(get_db)
):
    """Create a migration profile for a user."""
    
    user = db.query(User).filter(User.id == profile_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    profile = MigrationProfile(**profile_data.dict())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile


@router.get("/profiles/{user_id}", response_model=MigrationProfileResponse)
async def get_migration_profile(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a user's migration profile."""
    profile = db.query(MigrationProfile).filter(
        MigrationProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Migration profile not found"
        )
    
    return profile


@router.put("/profiles/{user_id}", response_model=MigrationProfileResponse)
async def update_migration_profile(
    user_id: UUID,
    profile_data: MigrationProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update a migration profile."""
    profile = db.query(MigrationProfile).filter(
        MigrationProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Migration profile not found"
        )
    
    for key, value in profile_data.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile


# ============================================
# ELIGIBILITY ENDPOINTS
# ============================================

@router.post("/eligibility", response_model=EligibilityResponse)
async def check_eligibility(
    request: EligibilityRequest,
    db: Session = Depends(get_db)
):
    """Check migration eligibility for a user profile."""
    
    # Get migration profile
    profile = db.query(MigrationProfile).filter(
        MigrationProfile.user_id == request.user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Migration profile not found. Please create one first."
        )
    
    # Get country
    country = db.query(Country).filter(
        Country.code == request.country_code
    ).first()
    
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    
    # Convert profile to dict
    profile_dict = {
        "age": profile.age,
        "nationality": profile.nationality,
        "country_of_residence": profile.country_of_residence,
        "education_level": profile.education_level,
        "field_of_study": profile.field_of_study,
        "years_experience": profile.years_experience,
        "english_level": profile.english_level,
        "english_test": profile.english_test,
        "english_score": profile.english_score,
        "occupation_title": profile.occupation_title,
        "occupation_code": profile.occupation_code,
        "target_countries": profile.target_countries,
        "target_visas": profile.target_visas,
    }
    
    # Run eligibility check
    result = migration_engine.evaluate_eligibility(
        profile_dict,
        request.country_code,
        request.visa_code
    )
    
    # Add disclaimer
    result["disclaimer"] = migration_engine.get_disclaimer()
    
    return result


@router.get("/disclaimer")
async def get_disclaimer():
    """Get the migration disclaimer."""
    return {
        "disclaimer": migration_engine.get_disclaimer()
    }


# ============================================
# SEED DATA ENDPOINT (Development Only)
# ============================================

@router.post("/seed")
async def seed_migration_data(
    db: Session = Depends(get_db)
):
    """Seed migration data (development only)."""
    from app.utils.seed_migration_data import seed_migration_data
    seed_migration_data(db)
    return {"message": "Migration data seeded successfully"}
