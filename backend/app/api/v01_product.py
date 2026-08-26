from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.career_profile import CareerProfile
from app.models.career_evidence import CareerEvidence
from app.models.job import Job
from app.models.persona import Persona
from app.models.v01_product import Application, CompanyIntelligence, Interview, TruthCheck, AuditLog, LiveInterviewSession

router = APIRouter(tags=["v0.1 Copilot"])

def audit(db, user, action, entity_type, entity_id=None, details=None):
    db.add(AuditLog(user_id=user.id, tenant_id=user.tenant_id, action=action, entity_type=entity_type, entity_id=entity_id, details=details or {}))

def words(text):
    return [w.lower() for w in text.replace("/", " ").replace(",", " ").split() if len(w) > 3]

class ProfileIn(BaseModel):
    name: str | None = None
    description: str | None = None
    target_roles: list[str] = Field(default_factory=list)
    seniority: str | None = None
    years_experience: int | None = None
    preferred_locations: list[str] = Field(default_factory=list)
    remote_preference: str | None = None
    salary_preferences: dict | None = None
    industries: list[str] = Field(default_factory=list)

class EvidenceIn(BaseModel):
    claim: str = Field(min_length=3)
    source_type: str = "user"
    source_file: str | None = None
    excerpt: str | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)

class ApplicationIn(BaseModel):
    job_id: str | None = None
    persona_id: str | None = None
    advertised_title: str
    company: str | None = None
    status: str = "DISCOVERED"
    notes: str | None = None

class CompanyIn(BaseModel):
    company_name: str
    role_context: str | None = None
    overview: str | None = None
    technology_signals: list[str] = Field(default_factory=list)
    leadership_signals: list[str] = Field(default_factory=list)
    culture_signals: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)

class InterviewIn(BaseModel):
    application_id: str
    round_type: str = "General"
    scheduled_at: datetime | None = None

class LiveIn(BaseModel):
    application_id: str

class AssistIn(BaseModel):
    question: str = Field(min_length=2)

@router.get("/career/profile")
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CareerProfile).filter(CareerProfile.user_id == user.id, CareerProfile.is_active.is_(True)).first()
    if not profile:
        return {"profile": None, "evidence": []}
    evidence = db.query(CareerEvidence).filter(CareerEvidence.career_profile_id == profile.id).all()
    return {"profile": profile, "evidence": evidence}

@router.post("/career/profile")
def save_profile(payload: ProfileIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CareerProfile).filter(CareerProfile.user_id == user.id, CareerProfile.is_active.is_(True)).first()
    data = payload.model_dump()
    if not profile:
        profile = CareerProfile(user_id=user.id, is_active=True)
        db.add(profile)
    for k,v in data.items(): setattr(profile, k, v)
    audit(db,user,"CAREER_PROFILE_UPDATED","career_profile",profile.id)
    db.commit(); db.refresh(profile)
    return profile

@router.post("/career/evidence")
def add_evidence(payload: EvidenceIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CareerProfile).filter(CareerProfile.user_id == user.id, CareerProfile.is_active.is_(True)).first()
    if not profile: raise HTTPException(400,"Create a Career Vault profile first")
    item = CareerEvidence(career_profile_id=profile.id, claim=payload.claim, source_type=payload.source_type, source_file=payload.source_file, excerpt=payload.excerpt, confidence=payload.confidence, verified_at=datetime.utcnow(), verified_by=str(user.id))
    db.add(item); audit(db,user,"CAREER_EVIDENCE_ADDED","career_evidence",item.id); db.commit(); db.refresh(item); return item

@router.get("/career/evidence")
def list_evidence(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CareerProfile).filter(CareerProfile.user_id == user.id, CareerProfile.is_active.is_(True)).first()
    return [] if not profile else db.query(CareerEvidence).filter(CareerEvidence.career_profile_id == profile.id).all()

@router.post("/applications")
def create_application(payload: ApplicationIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.get(Job, payload.job_id) if payload.job_id else None
    if job and job.user_id not in (None, user.id): raise HTTPException(403,"Job does not belong to this user")
    app = Application(user_id=user.id, tenant_id=user.tenant_id, job_id=payload.job_id, persona_id=payload.persona_id, advertised_title=payload.advertised_title, company=payload.company, status=payload.status, notes=payload.notes)
    db.add(app); audit(db,user,"APPLICATION_CREATED","application",app.id); db.commit(); db.refresh(app); return app

@router.get("/applications")
def list_applications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Application).filter(Application.user_id == user.id, Application.tenant_id == user.tenant_id).order_by(Application.created_at.desc()).all()

@router.patch("/applications/{application_id}/status")
def update_application_status(application_id: str, status_value: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == application_id, Application.user_id == user.id, Application.tenant_id == user.tenant_id).first()
    if not app: raise HTTPException(404,"Application not found")
    allowed={"DISCOVERED","ANALYZED","SHORTLISTED","READY_FOR_REVIEW","APPROVED","APPLIED","RECRUITER_CONTACT","INTERVIEW","OFFER","ACCEPTED","REJECTED","WITHDRAWN","ON_HOLD"}
    if status_value not in allowed: raise HTTPException(422,"Unsupported application state")
    app.status=status_value
    if status_value=="APPLIED": app.applied_at=datetime.utcnow()
    audit(db,user,"APPLICATION_STATUS_CHANGED","application",app.id,{"status":status_value}); db.commit(); db.refresh(app); return app

@router.post("/applications/{application_id}/package")
def generate_application_package(application_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id==application_id, Application.user_id==user.id, Application.tenant_id==user.tenant_id).first()
    if not app: raise HTTPException(404,"Application not found")
    evidence = list_evidence(user,db)
    claims=[e.claim for e in evidence]
    package={"advertised_title":app.advertised_title,"company":app.company,"resume_focus":claims[:12],"cover_letter":"Tailored from verified Career Vault evidence; review before submission.","application_answers":claims[:8],"recruiter_message":f"Interested in the {app.advertised_title} opportunity at {app.company or 'your organization'}."}
    app.package=package; app.status="READY_FOR_REVIEW"; audit(db,user,"APPLICATION_PACKAGE_GENERATED","application",app.id); db.commit(); db.refresh(app); return package

@router.post("/truth/{application_id}")
def truth_check(application_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app=db.query(Application).filter(Application.id==application_id,Application.user_id==user.id,Application.tenant_id==user.tenant_id).first()
    if not app: raise HTTPException(404,"Application not found")
    evidence=set(e.claim.lower() for e in list_evidence(user,db)); package=app.package or {}; text=" ".join(str(v) for v in package.values())
    claims=[c.strip() for c in text.split(".") if c.strip()]
    issues=[]
    for c in claims:
        if c and not any(token in c.lower() for token in [x for e in evidence for x in words(e)]): issues.append(c)
    result=TruthCheck(user_id=user.id,tenant_id=user.tenant_id,application_id=app.id,status="PASS" if not issues else "REVIEW",claims=claims,issues=issues)
    db.add(result); audit(db,user,"TRUTH_CHECK","truth_check",result.id,{"status":result.status}); db.commit(); db.refresh(result); return result

@router.post("/companies/intelligence")
def company_intelligence(payload: CompanyIn, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    item=CompanyIntelligence(user_id=user.id,tenant_id=user.tenant_id,company_name=payload.company_name,role_context=payload.role_context,overview=payload.overview,technology_signals=payload.technology_signals,leadership_signals=payload.leadership_signals,culture_signals=payload.culture_signals,sources=payload.sources)
    db.add(item); audit(db,user,"COMPANY_INTELLIGENCE_CREATED","company_intelligence",item.id); db.commit(); db.refresh(item); return item

@router.get("/companies/intelligence")
def companies(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    return db.query(CompanyIntelligence).filter(CompanyIntelligence.user_id==user.id,CompanyIntelligence.tenant_id==user.tenant_id).order_by(CompanyIntelligence.created_at.desc()).all()

@router.post("/interviews")
def create_interview(payload: InterviewIn,user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    app=db.query(Application).filter(Application.id==payload.application_id,Application.user_id==user.id,Application.tenant_id==user.tenant_id).first()
    if not app: raise HTTPException(404,"Application not found")
    questions=[f"Explain your approach to the {app.advertised_title} responsibilities.","Describe a difficult architecture decision you made.","Give an evidence-backed example of leadership and stakeholder management.","What risks would you assess in the target environment?"]
    prep={"technical":questions[:2],"behavioral":questions[2:],"evidence_to_review":[e.claim for e in list_evidence(user,db)[:8]]}
    item=Interview(user_id=user.id,tenant_id=user.tenant_id,application_id=app.id,round_type=payload.round_type,scheduled_at=payload.scheduled_at,questions=questions,preparation=prep)
    db.add(item); audit(db,user,"INTERVIEW_CREATED","interview",item.id); db.commit(); db.refresh(item); return item

@router.get("/interviews")
def interviews(user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    return db.query(Interview).filter(Interview.user_id==user.id,Interview.tenant_id==user.tenant_id).order_by(Interview.scheduled_at.asc().nullslast()).all()

@router.post("/live-interview/sessions")
def start_live(payload: LiveIn,user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    app=db.query(Application).filter(Application.id==payload.application_id,Application.user_id==user.id,Application.tenant_id==user.tenant_id).first()
    if not app: raise HTTPException(404,"Application not found")
    s=LiveInterviewSession(user_id=user.id,tenant_id=user.tenant_id,application_id=app.id,transcript=[],guidance=[])
    db.add(s); audit(db,user,"LIVE_INTERVIEW_STARTED","live_interview_session",s.id); db.commit(); db.refresh(s); return s

@router.post("/live-interview/sessions/{session_id}/assist")
def assist(session_id: str,payload: AssistIn,user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    s=db.query(LiveInterviewSession).filter(LiveInterviewSession.id==session_id,LiveInterviewSession.user_id==user.id,LiveInterviewSession.tenant_id==user.tenant_id).first()
    if not s: raise HTTPException(404,"Session not found")
    evidence=[e.claim for e in list_evidence(user,db)]
    q=payload.question
    relevant=[e for e in evidence if any(t in q.lower() for t in words(e))][:5]
    guidance={"question":q,"suggested_structure":["Answer directly","Give a verified example","Explain impact","State trade-offs"],"evidence":relevant,"warning":"Use only evidence-backed facts; do not invent metrics or experience."}
    s.transcript=(s.transcript or [])+[q]; s.guidance=(s.guidance or [])+[guidance]; db.commit(); db.refresh(s); return guidance

@router.get("/analytics/summary")
def analytics(user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    apps=db.query(Application).filter(Application.user_id==user.id,Application.tenant_id==user.tenant_id).all()
    ints=db.query(Interview).filter(Interview.user_id==user.id,Interview.tenant_id==user.tenant_id).all()
    profile=db.query(CareerProfile).filter(CareerProfile.user_id==user.id, CareerProfile.is_active.is_(True)).first()
    evidence=db.query(CareerEvidence).filter(CareerEvidence.career_profile_id==profile.id).count() if profile else 0
    return {"applications":len(apps),"interviews":len(ints),"evidence":evidence,"by_status":{s:sum(1 for a in apps if a.status==s) for s in sorted({a.status for a in apps})}}
