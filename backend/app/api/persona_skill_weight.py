from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.persona import Persona
from app.models.persona_skill_weight import PersonaSkillWeight
from app.models.skill import Skill
from app.schemas.persona_skill_weight import (
    PersonaSkillWeightCreate,
    PersonaSkillWeightUpdate,
    PersonaSkillWeightResponse
)

router = APIRouter(prefix="/personas/{persona_id}/skills", tags=["persona_skill_weights"])


@router.get("/", response_model=List[PersonaSkillWeightResponse])
async def list_skill_weights(
    persona_id: UUID,
    db: Session = Depends(get_db)
):
    """List all skill weights for a persona."""
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    weights = db.query(PersonaSkillWeight).filter(
        PersonaSkillWeight.persona_id == persona_id
    ).all()
    
    return weights


@router.post("/", response_model=PersonaSkillWeightResponse, status_code=status.HTTP_201_CREATED)
async def add_skill_weight(
    persona_id: UUID,
    weight_data: PersonaSkillWeightCreate,
    db: Session = Depends(get_db)
):
    """Add or update a skill weight for a persona."""
    # Verify persona exists
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    # Verify skill exists
    skill = db.query(Skill).filter(Skill.id == weight_data.skill_id).first()
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    # Check if weight already exists
    existing = db.query(PersonaSkillWeight).filter(
        PersonaSkillWeight.persona_id == persona_id,
        PersonaSkillWeight.skill_id == weight_data.skill_id
    ).first()
    
    if existing:
        # Update existing
        existing.weight = weight_data.weight
        existing.importance = weight_data.importance
        existing.notes = weight_data.notes
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new
    weight = PersonaSkillWeight(
        persona_id=persona_id,
        **weight_data.dict()
    )
    db.add(weight)
    db.commit()
    db.refresh(weight)
    
    return weight


@router.put("/{weight_id}", response_model=PersonaSkillWeightResponse)
async def update_skill_weight(
    persona_id: UUID,
    weight_id: UUID,
    weight_data: PersonaSkillWeightUpdate,
    db: Session = Depends(get_db)
):
    """Update a skill weight."""
    weight = db.query(PersonaSkillWeight).filter(
        PersonaSkillWeight.id == weight_id,
        PersonaSkillWeight.persona_id == persona_id
    ).first()
    
    if not weight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill weight not found"
        )
    
    for key, value in weight_data.dict(exclude_unset=True).items():
        setattr(weight, key, value)
    
    db.commit()
    db.refresh(weight)
    
    return weight


@router.delete("/{weight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill_weight(
    persona_id: UUID,
    weight_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a skill weight."""
    weight = db.query(PersonaSkillWeight).filter(
        PersonaSkillWeight.id == weight_id,
        PersonaSkillWeight.persona_id == persona_id
    ).first()
    
    if not weight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill weight not found"
        )
    
    db.delete(weight)
    db.commit()
    
    return None
