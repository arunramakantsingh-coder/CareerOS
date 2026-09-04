from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.career_fact_evidence import CareerFactEvidence
from app.models.career_profile import CareerProfile
from app.models.document import Document
from app.models.email_connector_account import EmailConnectorAccount
from app.models.persona import Persona
from app.models.persona_suggestion import PersonaSuggestion
from app.models.professional_experience import ProfessionalExperience
from app.models.user import User
from app.utils.document_ingestion import classify_document, extract_text

router = APIRouter(prefix="/identity", tags=["professional-identity"])
STORAGE_ROOT = Path(__import__("os").getenv("CAREEROS_STORAGE_ROOT", "/app/storage/documents")).resolve()


def profile_for(user: User, db: Session) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id, CandidateProfile.is_active.is_(True)).first()
    if not profile:
        profile = CandidateProfile(user_id=user.id, full_name=user.name, primary_email=user.email, reconciliation_status="pending")
        db.add(profile); db.commit(); db.refresh(profile)
    return profile


def fact_links(candidate_id: UUID, fact_type: str, fact_id: UUID, db: Session) -> list[dict[str, Any]]:
    rows = db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id == candidate_id, CareerFactEvidence.fact_type == fact_type, CareerFactEvidence.fact_id == fact_id).all()
    if not rows: return []
    docs = {d.id: d for d in db.query(Document).filter(Document.id.in_([x.document_id for x in rows])).all()}
    return [{"document_id": str(x.document_id), "filename": docs[x.document_id].original_filename if x.document_id in docs else None, "detected_type": docs[x.document_id].detected_type if x.document_id in docs else None, "confidence": x.confidence, "relationship": x.relationship, "excerpt": x.excerpt} for x in rows]


def document_summary(doc: Document, candidate_id: UUID, db: Session) -> dict[str, Any]:
    links = db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id == candidate_id, CareerFactEvidence.document_id == doc.id).all()
    classification = (doc.processing_status or {}).get("classification") or {}
    detected = doc.detected_type or (f"{doc.document_category}:{doc.document_subcategory}" if doc.document_subcategory else doc.document_category) or "other:unknown"
    return {
        "id": str(doc.id), "original_filename": doc.original_filename, "filename": doc.filename,
        "user_label": doc.user_label, "detected_type": detected, "category": doc.document_category,
        "subcategory": doc.document_subcategory, "issuer": doc.issuer,
        "issue_date": doc.issue_date, "expiry_date": doc.expiry_date, "document_number": doc.document_number,
        "classification_confidence": doc.classification_confidence or classification.get("confidence"),
        "classification_reason": doc.classification_reason or classification.get("reason"),
        "verification_status": doc.verification_status, "processing_stage": doc.processing_stage,
        "status": doc.status, "extraction_status": doc.extraction_status, "file_size": doc.file_size,
        "mime_type": doc.mime_type, "created_at": doc.created_at, "linked_fact_count": len(links),
    }


@router.get("/overview")
def identity_overview(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = profile_for(user, db)
    experiences = db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id == profile.id).order_by(ProfessionalExperience.start_date.desc().nullslast()).all()
    educations = db.query(CandidateEducation).filter(CandidateEducation.candidate_id == profile.id).all()
    certifications = db.query(CandidateCertification).filter(CandidateCertification.candidate_id == profile.id).all()
    skills = db.query(CandidateSkill).filter(CandidateSkill.candidate_id == profile.id).all()
    documents = db.query(Document).filter(Document.candidate_id == profile.id).order_by(Document.created_at.desc()).all()
    suggestions = db.query(PersonaSuggestion).filter(PersonaSuggestion.user_id == user.id, PersonaSuggestion.status == "suggested").order_by(PersonaSuggestion.confidence.desc()).all()

    def fact(item, fact_type):
        return {"id": str(item.id), **{k: getattr(item, k) for k in item.__table__.columns.keys() if k not in {"id", "candidate_id"}}, "evidence": fact_links(profile.id, fact_type, item.id, db)}

    section = {
        "personal": {"status": "complete" if profile.full_name and profile.title else "needs_review", "label": "Personal details & professional identity"},
        "resume": {"status": "complete" if any(d.document_category == "cv" for d in documents) else "needs_input", "label": "Resume & career positioning"},
        "employment": {"status": "complete" if experiences else "needs_input", "label": "Employment history"},
        "education": {"status": "complete" if educations else "needs_input", "label": "Education"},
        "certifications": {"status": "complete" if certifications else "pending", "label": "Certifications & credentials", "count": len(certifications)},
        "skills": {"status": "complete" if skills else "needs_input", "label": "IT skills & key skills", "count": len(skills)},
        "preferences": {"status": "needs_review" if not profile.work_preferences else "complete", "label": "Career profile & preferences"},
        "sources": {"status": "complete" if documents else "needs_input", "label": "Profile sources & next actions"},
    }
    evidence_count = db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id == profile.id).count()
    return {
        "profile": {"id": str(profile.id), "full_name": profile.full_name, "location": profile.location, "title": profile.title, "summary": profile.summary, "primary_email": profile.primary_email, "primary_phone": profile.primary_phone, "linkedin_url": profile.linkedin_url, "years_experience": profile.years_experience, "industries": profile.industries or [], "seniority": profile.seniority, "work_preferences": profile.work_preferences or {}, "completeness_score": profile.completeness_score or 0},
        "experiences": [fact(x, "employment") for x in experiences],
        "educations": [fact(x, "education") for x in educations],
        "certifications": [fact(x, "certification") for x in certifications],
        "skills": [fact(x, "skill") for x in skills],
        "documents": [document_summary(x, profile.id, db) for x in documents],
        "personas": [{"id": str(x.id), "name": x.name, "description": x.description, "positioning": x.positioning, "is_active": x.is_active, "target_titles": x.target_titles or []} for x in db.query(Persona).filter(Persona.user_id == user.id).all()],
        "persona_suggestions": [{"id": str(x.id), "name": x.name, "role_family": x.role_family, "positioning": x.positioning, "target_titles": x.target_titles or [], "confidence": x.confidence, "reason": x.reason, "missing_evidence": x.missing_evidence or [], "supporting_document_ids": x.supporting_document_ids or []} for x in suggestions],
        "section_navigation": section,
        "intelligence": {"profile_completeness": profile.completeness_score or 0, "evidence_coverage": round(min(100, evidence_count * 10), 1), "data_confidence": round(sum((x.confidence or 0) for x in certifications + educations + skills) / max(1, len(certifications) + len(educations) + len(skills)) * 100, 1), "persona_readiness": round(min(100, (len(experiences) * 20 + len(skills) * 5 + len(certifications) * 10)), 1)},
        "next_actions": _next_actions(profile, documents, experiences, educations, certifications, suggestions),
    }


def _next_actions(profile, documents, experiences, educations, certifications, suggestions):
    actions=[]
    if not any(d.document_category == "cv" for d in documents): actions.append({"key":"upload_cv","label":"Add your CV","detail":"CareerOS can build the first draft of your professional identity from it."})
    if experiences and not any(d.document_category == "employment" for d in documents): actions.append({"key":"employment_evidence","label":"Add employment evidence","detail":"Strengthen your timeline with an experience, offer or relieving letter."})
    if educations and not any(d.document_category == "education" for d in documents): actions.append({"key":"education_evidence","label":"Add education evidence","detail":"Link a degree, transcript or mark sheet when available."})
    if certifications and not any(d.document_category == "certification" for d in documents): actions.append({"key":"certification_evidence","label":"Add certification evidence","detail":"Link certificate documents to the credentials already found in your CV."})
    if suggestions: actions.append({"key":"review_personas","label":f"Review {len(suggestions)} persona suggestions","detail":"These are positioning lenses over the same evidence-backed career facts."})
    if not profile.work_preferences: actions.append({"key":"preferences","label":"Review career preferences","detail":"Add locations, work arrangement and target roles only where you have a preference."})
    return actions[:6]


@router.get("/evidence-library")
def evidence_library(user: User = Depends(get_current_user), db: Session = Depends(get_db), category: str | None = Query(None), verification: str | None = Query(None), search: str | None = Query(None)):
    profile = profile_for(user, db)
    docs = db.query(Document).filter(Document.candidate_id == profile.id).order_by(Document.created_at.desc()).all()
    result=[]
    for doc in docs:
        item=document_summary(doc,profile.id,db)
        if category and category != "all" and item["category"] != category: continue
        if verification and verification != "all" and item["verification_status"] != verification: continue
        if search and search.lower() not in " ".join(str(item.get(k) or "") for k in ("original_filename","filename","detected_type","issuer","classification_reason")).lower(): continue
        links=db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id==profile.id,CareerFactEvidence.document_id==doc.id).all()
        item["linked_facts"]=[{"fact_type":x.fact_type,"fact_id":str(x.fact_id),"relationship":x.relationship,"confidence":x.confidence} for x in links]
        result.append(item)
    return {"documents":result,"filters":{"categories":["all","cv","employment","education","certification","achievement","project","reference","other"],"verification":["all","reported","verified","needs_confirmation","conflicting"]}}


@router.get("/documents/{document_id}")
def document_detail(document_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile=profile_for(user,db); doc=db.query(Document).filter(Document.id==document_id,Document.candidate_id==profile.id).first()
    if not doc: raise HTTPException(404,"Document not found")
    item=document_summary(doc,profile.id,db)
    item["source_metadata"]={k:v for k,v in (doc.source_metadata or {}).items() if k not in {"extracted_text"}}
    item["linked_facts"]=[]
    for link in db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id==profile.id,CareerFactEvidence.document_id==doc.id).all(): item["linked_facts"].append({"fact_type":link.fact_type,"fact_id":str(link.fact_id),"confidence":link.confidence,"excerpt":link.excerpt})
    return item


@router.get("/documents/{document_id}/content")
def document_content(document_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile=profile_for(user,db); doc=db.query(Document).filter(Document.id==document_id,Document.candidate_id==profile.id).first()
    if not doc: raise HTTPException(404,"Document not found")
    path=Path(doc.storage_path).resolve()
    if STORAGE_ROOT not in path.parents or not path.is_file(): raise HTTPException(404,"Stored document is unavailable")
    return FileResponse(path=str(path), media_type=doc.mime_type or "application/octet-stream", filename=doc.original_filename)


@router.post("/documents/{document_id}/reclassify")
def reclassify_document(document_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile=profile_for(user,db); doc=db.query(Document).filter(Document.id==document_id,Document.candidate_id==profile.id).first()
    if not doc: raise HTTPException(404,"Document not found")
    path=Path(doc.storage_path).resolve()
    if STORAGE_ROOT not in path.parents or not path.is_file(): raise HTTPException(404,"Stored document is unavailable")
    text,meta=extract_text(doc.original_filename,doc.mime_type,path.read_bytes())
    result=classify_document(doc.original_filename,text)
    doc.document_category=result["category"]; doc.document_subcategory=result["subcategory"]; doc.document_type=result["subcategory"]; doc.detected_type=f"{result['category']}:{result['subcategory']}"; doc.classification_confidence=result["confidence"]; doc.classification_reason=result["reason"]; doc.processing_status={**(doc.processing_status or {}),"classification":result,"extraction":meta}; db.commit(); db.refresh(doc)
    return document_summary(doc,profile.id,db)


@router.post("/personas/suggestions/generate")
def generate_persona_suggestions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile=profile_for(user,db)
    experiences=db.query(ProfessionalExperience).filter(ProfessionalExperience.candidate_id==profile.id).all()
    skills=db.query(CandidateSkill).filter(CandidateSkill.candidate_id==profile.id).all()
    certs=db.query(CandidateCertification).filter(CandidateCertification.candidate_id==profile.id).all()
    docs=db.query(Document).filter(Document.candidate_id==profile.id,Document.document_category=="cv").all()
    corpus=" ".join([profile.title or "",profile.summary or ""]+[x.title+" "+x.company+" "+" ".join(x.responsibilities or []) for x in experiences]+[x.name for x in skills]+[x.name for x in certs]).lower()
    patterns=[
        ("Cloud & Infrastructure",["cloud","aws","azure","gcp","infrastructure","kubernetes","vmware"],["Cloud Architect","Cloud Infrastructure Architect","Infrastructure Architect"]),
        ("Cybersecurity",["security","cybersecurity","siem","zero trust","incident response","cissp","cism","cisa"],["Cybersecurity Architect","Cloud Security Architect","Security Transformation Leader"]),
        ("Network & Connectivity",["network","routing","switching","bgp","sd-wan","mpls","firewall"],["Network Architect","Network & Security Architect","Connectivity Leader"]),
        ("Technology Leadership",["director","vp","head of","leader","leadership","governance","transformation","manager"],["Enterprise Technology Leader","Technology Transformation Leader","Infrastructure & Operations Leader"]),
        ("Architecture",["architect","architecture","enterprise architecture","solution architecture"],["Enterprise Architect","Solution Architect","Technology Architect"]),
    ]
    existing={s.name for s in db.query(PersonaSuggestion).filter(PersonaSuggestion.user_id==user.id,PersonaSuggestion.status=="suggested").all()}
    created=[]
    for family,terms,titles in patterns:
        hits=[t for t in terms if t in corpus]
        if not hits: continue
        confidence=min(0.94,0.50+0.08*len(hits)+0.03*min(len(experiences),5)+0.02*min(len(certs),4))
        name=titles[0]
        if name in existing: continue
        supporting_docs=[str(x.id) for x in docs]
        reason=f"Suggested because your career evidence contains signals for {family}: {', '.join(hits[:5])}."
        missing=[]
        if not certs: missing.append("Add or confirm relevant credentials if you hold them")
        if not experiences: missing.append("Add employment history")
        suggestion=PersonaSuggestion(id=uuid4(),user_id=user.id,candidate_id=profile.id,name=name,role_family=family,positioning=f"Position the same Career Vault evidence around {name.lower()} outcomes without changing the underlying facts.",target_titles=titles,supporting_fact_ids=[str(x.id) for x in experiences+skills+certs],supporting_document_ids=supporting_docs,missing_evidence=missing,confidence=confidence,reason=reason,status="suggested")
        db.add(suggestion); created.append(suggestion); existing.add(name)
    db.commit()
    return [{"id":str(x.id),"name":x.name,"role_family":x.role_family,"positioning":x.positioning,"target_titles":x.target_titles or [],"confidence":x.confidence,"reason":x.reason,"missing_evidence":x.missing_evidence or [],"supporting_document_ids":x.supporting_document_ids or []} for x in created]


@router.get("/personas/suggestions")
def persona_suggestions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows=db.query(PersonaSuggestion).filter(PersonaSuggestion.user_id==user.id).order_by(PersonaSuggestion.confidence.desc()).all()
    return [{"id":str(x.id),"name":x.name,"role_family":x.role_family,"positioning":x.positioning,"target_titles":x.target_titles or [],"confidence":x.confidence,"reason":x.reason,"missing_evidence":x.missing_evidence or [],"status":x.status,"supporting_document_ids":x.supporting_document_ids or []} for x in rows]


def ensure_career_profile(user: User, candidate: CandidateProfile, db: Session) -> CareerProfile:
    cp=db.query(CareerProfile).filter(CareerProfile.user_id==user.id,CareerProfile.is_active.is_(True)).first()
    if not cp:
        cp=CareerProfile(user_id=user.id,is_active=True)
        db.add(cp)
    cp.name=candidate.full_name or cp.name; cp.description=candidate.summary or cp.description; cp.seniority=candidate.seniority or cp.seniority
    cp.years_experience=int(candidate.years_experience) if candidate.years_experience else cp.years_experience
    cp.preferred_locations=(candidate.work_preferences or {}).get("preferred_locations") or cp.preferred_locations
    cp.remote_preference=(candidate.work_preferences or {}).get("remote_preference") or cp.remote_preference
    cp.target_roles=(candidate.work_preferences or {}).get("target_roles") or cp.target_roles
    cp.industries=candidate.industries or cp.industries
    db.flush(); return cp


@router.post("/personas/suggestions/{suggestion_id}/activate")
def activate_persona_suggestion(suggestion_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile=profile_for(user,db); suggestion=db.query(PersonaSuggestion).filter(PersonaSuggestion.id==suggestion_id,PersonaSuggestion.user_id==user.id,PersonaSuggestion.candidate_id==profile.id).first()
    if not suggestion: raise HTTPException(404,"Persona suggestion not found")
    cp=ensure_career_profile(user,profile,db)
    persona=Persona(user_id=user.id,career_profile_id=cp.id,name=suggestion.name,description=suggestion.reason,positioning=suggestion.positioning,target_titles=suggestion.target_titles,target_industries=profile.industries or [],target_locations=(profile.work_preferences or {}).get("preferred_locations") or [],preferred_seniority=profile.seniority,remote_preference=(profile.work_preferences or {}).get("remote_preference") or "Any",is_active=False,is_default=False,keywords=[])
    db.add(persona); suggestion.status="activated"; db.commit(); db.refresh(persona)
    return {"id":str(persona.id),"name":persona.name,"status":"activated"}


@router.get("/connections/diagnostics")
def connection_diagnostics(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows=db.query(EmailConnectorAccount).filter(EmailConnectorAccount.user_id==user.id).all()
    external=[]
    for x in db.query(__import__("app.models.external_identity",fromlist=["ExternalIdentity"]).ExternalIdentity).filter(__import__("app.models.external_identity",fromlist=["ExternalIdentity"]).ExternalIdentity.user_id==user.id, __import__("app.models.external_identity",fromlist=["ExternalIdentity"]).ExternalIdentity.is_active.is_(True)).all():
        external.append({"id":str(x.id),"provider":x.provider,"provider_email":x.provider_email,"scopes":x.scopes or [],"token_status":"present" if x.access_token else "missing","token_expires_at":x.token_expires_at,"last_used":x.last_used})
    return {"email_sources":[{"id":str(x.id),"provider":x.provider,"email_address":x.email_address,"status":x.status,"auth_method":x.auth_method,"capabilities":x.capabilities or {},"scopes":x.scopes or [],"token_expires_at":x.token_expires_at,"last_sync_at":x.last_sync_at,"last_sync_status":x.last_sync_status,"last_error_code":x.last_error_code,"last_error_message":x.last_error_message} for x in rows],"external_identities":external,"provider_catalog":[{"provider":"google","label":"Gmail / Google Workspace","status":"available","capabilities":["read_messages","read_threads","search_messages"]},{"provider":"microsoft","label":"Outlook / Microsoft 365","status":"available","capabilities":["read_messages","read_threads","search_messages"]},{"provider":"imap","label":"IMAP / SMTP","status":"coming_later","capabilities":["read_messages","search_messages","send_message"]},{"provider":"yahoo","label":"Yahoo Mail","status":"coming_later","capabilities":["read_messages","search_messages"]},{"provider":"icloud","label":"iCloud Mail","status":"coming_later","capabilities":["read_messages","search_messages"]}]}
