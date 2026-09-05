from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.candidate_profile import CandidateProfile
from app.models.career_profile import CareerProfile
from app.models.persona import Persona
from app.models.user import User

router = APIRouter(prefix="/persona-builder", tags=["persona-builder"])


class PersonaBuildIn(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    positioning: str | None = None
    target_titles: list[str] = Field(default_factory=list)


@router.post("/build")
def build_persona(payload: PersonaBuildIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    candidate = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id, CandidateProfile.is_active.is_(True)).first()
    if not candidate: raise ValueError("Create a professional profile before creating a persona")
    career = db.query(CareerProfile).filter(CareerProfile.user_id == user.id, CareerProfile.is_active.is_(True)).first()
    if not career:
        career = CareerProfile(user_id=user.id, name=candidate.full_name, description=candidate.summary, seniority=candidate.seniority, years_experience=int(candidate.years_experience) if candidate.years_experience else None, preferred_locations=(candidate.work_preferences or {}).get("preferred_locations") or [], remote_preference=(candidate.work_preferences or {}).get("work_arrangement") or "Any", target_roles=(candidate.work_preferences or {}).get("target_roles") or [], industries=candidate.industries or [], is_active=True)
        db.add(career); db.flush()
    persona = Persona(user_id=user.id, career_profile_id=career.id, name=payload.name, positioning=payload.positioning or f"Positioning lens for {payload.name} using the same evidence-backed Career Vault facts.", description="Manual persona built over the canonical Career Vault.", target_titles=payload.target_titles or [payload.name], target_industries=candidate.industries or [], target_locations=(candidate.work_preferences or {}).get("preferred_locations") or [], preferred_seniority=candidate.seniority, remote_preference=(candidate.work_preferences or {}).get("work_arrangement") or "Any", is_active=False, is_default=False)
    db.add(persona); db.commit(); db.refresh(persona)
    return {"id": str(persona.id), "name": persona.name, "is_active": persona.is_active}
