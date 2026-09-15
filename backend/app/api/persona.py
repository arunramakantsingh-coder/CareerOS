from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.persona import Persona
from app.models.persona_skill_weight import PersonaSkillWeight
from app.models.user import User
from app.models.skill import Skill
from app.models.career_profile import CareerProfile
from app.schemas.persona import PersonaCreate, PersonaUpdate, PersonaResponse
from app.schemas.persona_skill_weight import PersonaSkillWeightCreate, PersonaSkillWeightResponse

router = APIRouter(prefix="/personas", tags=["personas"])


def owned_persona(persona_id: UUID, user: User, db: Session) -> Persona:
    persona = db.query(Persona).filter(Persona.id == persona_id, Persona.user_id == user.id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona


@router.get("/", response_model=List[PersonaResponse])
async def list_personas(user_id: Optional[UUID] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id and user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(Persona).filter(Persona.user_id == current_user.id).order_by(Persona.created_at.desc()).all()


@router.get("/active", response_model=Optional[PersonaResponse])
async def get_active_persona(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Persona).filter(Persona.user_id == current_user.id, Persona.is_active.is_(True)).first()


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(persona_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return owned_persona(persona_id, current_user, db)


@router.post("/", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
async def create_persona(persona_data: PersonaCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    career_profile = db.query(CareerProfile).filter(CareerProfile.id == persona_data.career_profile_id, CareerProfile.user_id == current_user.id).first()
    if not career_profile:
        raise HTTPException(status_code=403, detail="Career profile does not belong to the current user")
    data = persona_data.dict()
    data["user_id"] = current_user.id
    persona = Persona(**data)
    db.add(persona); db.commit(); db.refresh(persona)
    return persona


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(persona_id: UUID, persona_data: PersonaUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    persona = owned_persona(persona_id, current_user, db)
    for key, value in persona_data.dict(exclude_unset=True).items(): setattr(persona, key, value)
    db.commit(); db.refresh(persona)
    return persona


@router.post("/{persona_id}/activate")
async def activate_persona(persona_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    persona = owned_persona(persona_id, current_user, db)
    db.query(Persona).filter(Persona.user_id == current_user.id).update({"is_active": False})
    persona.is_active = True
    db.commit()
    return {"message": f"Persona '{persona.name}' activated successfully"}


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_persona(persona_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    persona = owned_persona(persona_id, current_user, db)
    db.delete(persona); db.commit()
    return None
