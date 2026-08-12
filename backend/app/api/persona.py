from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.persona import Persona
from app.models.persona_skill_weight import PersonaSkillWeight
from app.models.user import User
from app.models.skill import Skill
from app.schemas.persona import PersonaCreate, PersonaUpdate, PersonaResponse
from app.schemas.persona_skill_weight import PersonaSkillWeightCreate, PersonaSkillWeightResponse

router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("/", response_model=List[PersonaResponse])
async def list_personas(
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """List all personas for a user."""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id is required"
        )
    
    personas = db.query(Persona).filter(Persona.user_id == user_id).all()
    return personas


@router.get("/active", response_model=Optional[PersonaResponse])
async def get_active_persona(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get the currently active persona for a user."""
    persona = db.query(Persona).filter(
        Persona.user_id == user_id,
        Persona.is_active == True
    ).first()
    
    if not persona:
        return None
    
    return persona


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific persona by ID."""
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    return persona


@router.post("/", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
async def create_persona(
    persona_data: PersonaCreate,
    db: Session = Depends(get_db)
):
    """Create a new persona."""
    # Verify user exists
    user = db.query(User).filter(User.id == persona_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create persona
    persona = Persona(**persona_data.dict())
    db.add(persona)
    db.commit()
    db.refresh(persona)
    
    return persona


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: UUID,
    persona_data: PersonaUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing persona."""
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    # Update fields
    for key, value in persona_data.dict(exclude_unset=True).items():
        setattr(persona, key, value)
    
    db.commit()
    db.refresh(persona)
    
    return persona


@router.post("/{persona_id}/activate")
async def activate_persona(
    persona_id: UUID,
    db: Session = Depends(get_db)
):
    """Activate a persona (deactivate all others for the user)."""
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    # Deactivate all personas for this user
    db.query(Persona).filter(Persona.user_id == persona.user_id).update(
        {"is_active": False}
    )
    
    # Activate this persona
    persona.is_active = True
    db.commit()
    
    return {"message": f"Persona '{persona.name}' activated successfully"}


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_persona(
    persona_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a persona."""
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    db.delete(persona)
    db.commit()
    
    return None
