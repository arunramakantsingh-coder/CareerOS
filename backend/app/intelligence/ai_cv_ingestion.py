from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.intelligence.contracts import IntelligenceRequest
from app.intelligence.engine import engine
from app.intelligence.identity_reconciliation import EMPLOYMENT_SCHEMA, _sanitize_experience
from app.intelligence.safe_employment_reconciliation import apply_experiences_source_scoped
from app.models.candidate_certification import CandidateCertification
from app.models.candidate_education import CandidateEducation
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.career_fact_evidence import CareerFactEvidence
from app.models.document import Document
from app.models.persona_suggestion import PersonaSuggestion


SCHEMA: dict[str, Any] = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "profile": {"type":"object","additionalProperties":False,"properties":{
            "full_name":{"type":["string","null"]},"location":{"type":["string","null"]},"title":{"type":["string","null"]},"summary":{"type":["string","null"]},"primary_email":{"type":["string","null"]},"primary_phone":{"type":["string","null"]},"linkedin_url":{"type":["string","null"]},"years_experience":{"type":["number","null"]},"industries":{"type":"array","items":{"type":"string"},"maxItems":20},"seniority":{"type":["string","null"]}},
            "required":["full_name","location","title","summary","primary_email","primary_phone","linkedin_url","years_experience","industries","seniority"]},
        "experiences": EMPLOYMENT_SCHEMA["properties"]["experiences"],
        "skills":{"type":"array","maxItems":100,"items":{"type":"object","additionalProperties":False,"properties":{"name":{"type":"string"},"category":{"type":["string","null"]},"proficiency":{"type":["string","null"]},"years_experience":{"type":["number","null"]},"last_used":{"type":["string","null"]},"confidence":{"type":"number","minimum":0,"maximum":1},"evidence_excerpt":{"type":["string","null"]}},"required":["name","category","proficiency","years_experience","last_used","confidence","evidence_excerpt"]}},
        "certifications":{"type":"array","maxItems":50,"items":{"type":"object","additionalProperties":False,"properties":{"name":{"type":"string"},"issuer":{"type":"string"},"issue_date":{"type":["string","null"]},"expiry_date":{"type":["string","null"]},"credential_reference":{"type":["string","null"]},"credential_url":{"type":["string","null"]},"confidence":{"type":"number","minimum":0,"maximum":1},"evidence_excerpt":{"type":["string","null"]}},"required":["name","issuer","issue_date","expiry_date","credential_reference","credential_url","confidence","evidence_excerpt"]}},
        "education":{"type":"array","maxItems":20,"items":{"type":"object","additionalProperties":False,"properties":{"institution":{"type":"string"},"degree":{"type":"string"},"field_of_study":{"type":["string","null"]},"start_date":{"type":["string","null"]},"end_date":{"type":["string","null"]},"is_current":{"type":"boolean"},"grade":{"type":["string","null"]},"confidence":{"type":"number","minimum":0,"maximum":1},"evidence_excerpt":{"type":["string","null"]}},"required":["institution","degree","field_of_study","start_date","end_date","is_current","grade","confidence","evidence_excerpt"]}},
        "personas":{"type":"array","maxItems":10,"items":{"type":"object","additionalProperties":False,"properties":{"name":{"type":"string"},"role_family":{"type":["string","null"]},"positioning":{"type":"string"},"target_titles":{"type":"array","items":{"type":"string"},"maxItems":10},"confidence":{"type":"number","minimum":0,"maximum":1},"reason":{"type":"string"}},"required":["name","role_family","positioning","target_titles","confidence","reason"]}},
    },
    "required":["profile","experiences","skills","certifications","education","personas"],
}


class AICVIngestionError(RuntimeError):
    pass


def ingest_cv_with_ai(document: Document, profile: CandidateProfile, db: Session) -> dict[str, Any]:
    text = (document.source_metadata or {}).get("extracted_text", "")
    if not isinstance(text, str) or not text.strip():
        raise AICVIngestionError("No extracted document text is available")
    task = """Read the COMPLETE CV semantically and build a structured CareerOS career profile. AI extraction is primary: do not depend on deterministic parsers or exact headings because PDF text can be flattened or malformed. Extract every supported employment role, including multiple roles at one employer; preserve employer, optional client, title and dates. Extract profile identity, skills, certifications and education. Generate professional persona proposals grounded in the extracted evidence. Do not invent facts. Do not convert skills/projects/summary phrases into jobs. Use null/empty when absent. Return JSON only matching the schema."""
    request = IntelligenceRequest(task=task, context={"document":{"id":str(document.id),"filename":document.original_filename,"category":document.document_category,"text":text[:100000]}}, output_schema=SCHEMA, tools=["document_lookup","career_vault_search","evidence_search"], temperature=0.0)
    result = _run(request)
    if result.status != "completed":
        detail = result.result if isinstance(result.result, dict) else {"error": str(result.result)}
        raise AICVIngestionError(f"AI CV extraction failed: {detail}")
    payload = _parse(result.result)
    counts = _persist(document, profile, payload, db)
    metadata = dict(document.source_metadata or {})
    metadata["ai_profile_extraction"] = {"status":"completed","engine_version":result.engine_version,"provider":result.provider,"model":result.model,"trace_id":str(result.trace_id) if result.trace_id else None,"counts":counts,"payload":payload}
    document.source_metadata = metadata
    profile.reconciliation_status = "complete" if counts["needs_review"] == 0 else "conflicting"
    db.commit()
    return {"status":profile.reconciliation_status,"document_id":str(document.id),"model":result.model,"provider":result.provider,"trace_id":str(result.trace_id) if result.trace_id else None,"counts":counts}


def _persist(document: Document, profile: CandidateProfile, payload: dict[str, Any], db: Session) -> dict[str,int]:
    p=payload.get("profile") or {}
    for field in ("full_name","location","title","summary","primary_email","primary_phone","linkedin_url","years_experience","seniority"):
        value=p.get(field)
        if value not in (None,"",[]) and getattr(profile,field,None) in (None,"",0): setattr(profile,field,value)
    profile.industries=_merge(profile.industries or [],p.get("industries") or [])
    raw=[_sanitize_experience(x) for x in payload.get("experiences",[]) if isinstance(x,dict)]
    applied,review,protected=apply_experiences_source_scoped(document,raw,db)
    for x in payload.get("skills",[]): _skill(document,profile,x,db)
    for x in payload.get("certifications",[]): _cert(document,profile,x,db)
    for x in payload.get("education",[]): _edu(document,profile,x,db)
    for x in payload.get("personas",[]): _persona(document,profile,x,db)
    return {"experiences":len(applied),"needs_review":len(review),"protected":len(protected),"skills":len(payload.get("skills",[])),"certifications":len(payload.get("certifications",[])),"education":len(payload.get("education",[])),"personas":len(payload.get("personas",[]))}


def _skill(doc,profile,x,db):
    name=_clean(x.get("name"));
    if not name:return
    row=db.query(CandidateSkill).filter(CandidateSkill.candidate_id==profile.id,CandidateSkill.name.ilike(name)).first()
    if not row: row=CandidateSkill(candidate_id=profile.id,name=name,source_type="cv_ai",source_id=doc.id); db.add(row)
    row.category=row.category or _clean(x.get("category")); row.proficiency=row.proficiency or _clean(x.get("proficiency")); row.years_experience=row.years_experience or x.get("years_experience"); row.last_used=row.last_used or _clean(x.get("last_used")); row.confidence=max(float(row.confidence or 0),float(x.get("confidence") or .7)); db.flush(); _evidence(profile.id,doc,"skill",row.id,x.get("confidence"),x.get("evidence_excerpt"),db)


def _cert(doc,profile,x,db):
    name=_clean(x.get("name")); issuer=_clean(x.get("issuer")) or "Unknown"
    if not name:return
    row=db.query(CandidateCertification).filter(CandidateCertification.candidate_id==profile.id,CandidateCertification.name.ilike(name)).first()
    if not row: row=CandidateCertification(candidate_id=profile.id,name=name,issuer=issuer,source_type="cv_ai",source_id=doc.id); db.add(row)
    row.issuer=row.issuer if row.issuer!="Unknown" else issuer; row.issue_date=row.issue_date or _date(x.get("issue_date")); row.expiry_date=row.expiry_date or _date(x.get("expiry_date")); row.credential_reference=row.credential_reference or _clean(x.get("credential_reference")); row.credential_url=row.credential_url or _clean(x.get("credential_url")); row.confidence=max(float(row.confidence or 0),float(x.get("confidence") or .7)); db.flush(); _evidence(profile.id,doc,"certification",row.id,x.get("confidence"),x.get("evidence_excerpt"),db)


def _edu(doc,profile,x,db):
    institution=_clean(x.get("institution")); degree=_clean(x.get("degree"))
    if not institution or not degree:return
    row=db.query(CandidateEducation).filter(CandidateEducation.candidate_id==profile.id,CandidateEducation.institution.ilike(institution),CandidateEducation.degree.ilike(degree)).first()
    if not row: row=CandidateEducation(candidate_id=profile.id,institution=institution,degree=degree,source_type="cv_ai",source_id=doc.id); db.add(row)
    row.field_of_study=row.field_of_study or _clean(x.get("field_of_study")); row.start_date=row.start_date or _date(x.get("start_date")); row.end_date=row.end_date or _date(x.get("end_date")); row.grade=row.grade or _clean(x.get("grade")); row.confidence=max(float(row.confidence or 0),float(x.get("confidence") or .7)); db.flush(); _evidence(profile.id,doc,"education",row.id,x.get("confidence"),x.get("evidence_excerpt"),db)


def _persona(doc,profile,x,db):
    name=_clean(x.get("name"));
    if not name:return
    row=db.query(PersonaSuggestion).filter(PersonaSuggestion.user_id==profile.user_id,PersonaSuggestion.candidate_id==profile.id,PersonaSuggestion.name==name,PersonaSuggestion.status=="suggested").first()
    if not row: row=PersonaSuggestion(user_id=profile.user_id,candidate_id=profile.id,name=name,status="suggested"); db.add(row)
    row.role_family=_clean(x.get("role_family")); row.positioning=_clean(x.get("positioning")); row.target_titles=x.get("target_titles") or []; row.confidence=float(x.get("confidence") or .7); row.reason=_clean(x.get("reason")); row.supporting_document_ids=[str(doc.id)]


def _evidence(candidate_id,doc,kind,fact_id,confidence,excerpt,db):
    row=db.query(CareerFactEvidence).filter(CareerFactEvidence.candidate_id==candidate_id,CareerFactEvidence.document_id==doc.id,CareerFactEvidence.fact_type==kind,CareerFactEvidence.fact_id==fact_id).first()
    if row: row.confidence=max(row.confidence,float(confidence or .7)); row.excerpt=_clean(excerpt) or row.excerpt; return
    db.add(CareerFactEvidence(candidate_id=candidate_id,document_id=doc.id,fact_type=kind,fact_id=fact_id,relationship="supports",confidence=float(confidence or .7),excerpt=_clean(excerpt)))


def _merge(existing, incoming):
    result=list(existing); seen={re.sub(r"[^a-z0-9]+"," ",str(x).lower()).strip() for x in result}
    for x in incoming:
        if isinstance(x,str) and x.strip() and re.sub(r"[^a-z0-9]+"," ",x.lower()).strip() not in seen: result.append(x.strip()); seen.add(re.sub(r"[^a-z0-9]+"," ",x.lower()).strip())
    return result


def _clean(x): return str(x).strip() if x not in (None,"") else None


def _date(x):
    if not x or not isinstance(x,str): return None
    for fmt in ("%Y-%m-%d","%Y-%m","%B %Y","%b %Y","%Y"):
        try:return datetime.strptime(x.strip(),fmt)
        except ValueError:pass
    return None


def _parse(x):
    if isinstance(x,dict): return x
    if not isinstance(x,str): raise AICVIngestionError("Local AI returned an invalid CV extraction payload")
    x=x.strip(); x=re.sub(r"^```(?:json)?\s*","",x,flags=re.I); x=re.sub(r"\s*```$","",x)
    try:return json.loads(x)
    except json.JSONDecodeError as exc:raise AICVIngestionError(f"Local AI returned invalid JSON: {exc}") from exc


def _run(request):
    try:return asyncio.run(engine.execute(request))
    except RuntimeError as exc:
        if "asyncio.run() cannot be called" not in str(exc):raise
        loop=asyncio.new_event_loop()
        try:return loop.run_until_complete(engine.execute(request))
        finally:loop.close()
