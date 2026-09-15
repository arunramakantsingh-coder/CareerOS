from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.roles import require_developer
from app.intelligence.ai_cv_ingestion import _normalize_payload, _parse, _persist, _prepare_cv_text
from app.intelligence.contracts import IntelligenceRequest
from app.intelligence.engine import engine
from app.models.candidate_profile import CandidateProfile
from app.models.document import Document
from app.models.user import User

router = APIRouter(prefix="/developer/cv-json-lab", tags=["developer-cv-json-lab"])


class CVJsonLabRequest(BaseModel):
    document_id: UUID | None = None
    instruction: str = Field(min_length=1, max_length=12000)
    template: dict[str, Any]
    cv_text_override: str | None = Field(default=None, max_length=120000)


def _compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)


def _looks_like_schema(value: Any) -> bool:
    return isinstance(value, dict) and value.get("type") == "object" and isinstance(value.get("properties"), dict)


def _template_to_schema(value: Any) -> dict[str, Any]:
    if _looks_like_schema(value):
        return value
    if isinstance(value, dict):
        properties = {key: _template_to_schema(item) for key, item in value.items()}
        return {"type": "object", "additionalProperties": False, "properties": properties, "required": list(properties.keys())}
    if isinstance(value, list):
        return {"type": "array", "items": _template_to_schema(value[0]) if value else {}}
    if value is None:
        return {"type": ["string", "null"]}
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, (int, float)):
        return {"type": "number"}
    return {"type": "string"}


def _profile_for(user: User, db: Session) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id, CandidateProfile.is_active.is_(True)).first()
    if not profile:
        raise HTTPException(404, "Professional profile not found")
    return profile


def _cv_documents(profile: CandidateProfile, db: Session) -> list[Document]:
    return db.query(Document).filter(Document.candidate_id == profile.id, Document.document_category == "cv").order_by(Document.created_at.desc()).all()


def _source_payload(document: Document, text: str | None = None) -> dict[str, Any]:
    source_text = _prepare_cv_text(text if text is not None else (document.source_metadata or {}).get("extracted_text", ""))
    return {"id": str(document.id), "filename": document.original_filename, "stored_filename": document.filename, "category": document.document_category, "processing_stage": document.processing_stage, "extraction_status": document.extraction_status, "created_at": document.created_at.isoformat() if document.created_at else None, "chars": len(source_text), "words": len(source_text.split()) if source_text else 0, "has_extracted_text": bool(source_text)}


@router.get("/source")
def source_documents(user: User = Depends(require_developer), db: Session = Depends(get_db)):
    profile = _profile_for(user, db)
    documents = _cv_documents(profile, db)
    return {"selected_document_id": str(documents[0].id) if documents else None, "documents": [_source_payload(document) for document in documents]}


@router.post("/extract")
async def extract_cv_json(request: CVJsonLabRequest, user: User = Depends(require_developer), db: Session = Depends(get_db)):
    profile = _profile_for(user, db)
    documents = _cv_documents(profile, db)
    if not documents:
        raise HTTPException(404, "No uploaded CV was found in Document Vault")

    document = next((item for item in documents if request.document_id and item.id == request.document_id), documents[0])
    vault_text = _prepare_cv_text((document.source_metadata or {}).get("extracted_text", ""))
    text = _prepare_cv_text(request.cv_text_override) if request.cv_text_override is not None else vault_text
    if not text:
        raise HTTPException(422, "The selected uploaded CV has no extracted text")

    compact_template = _compact(request.template)
    schema = _template_to_schema(request.template)
    compact_instruction = " ".join(request.instruction.split())
    prompt = _compact({"instruction": f"{compact_instruction} Return minified JSON only; no markdown or commentary.", "format": request.template, "cv": text})

    result = await engine.execute(IntelligenceRequest(task=prompt, task_type="cv_extraction", context={}, output_schema=schema, tools=[], temperature=0.0))
    if result.status != "completed":
        raise HTTPException(422, f"CV JSON extraction failed: {result.result}")

    try:
        parsed = _parse(result.result)
    except Exception as exc:
        raise HTTPException(422, str(exc)) from exc

    normalized = _normalize_payload(parsed)
    savepoint = db.begin_nested()
    try:
        would_apply = _persist(document, profile, normalized, db)
    finally:
        savepoint.rollback()
        db.expire_all()

    compact_output = _compact(parsed)
    expected_sections = list(request.template.keys())
    actual_sections = list(parsed.keys()) if isinstance(parsed, dict) else []
    missing_sections = [key for key in expected_sections if key not in actual_sections]

    return {
        "status": "completed",
        "document": _source_payload(document, text),
        "source_mode": "debug_override" if request.cv_text_override is not None else "document_vault",
        "provider": result.provider,
        "model": result.model,
        "trace_id": str(result.trace_id) if result.trace_id else None,
        "output": compact_output,
        "output_json": parsed,
        "validation": {"valid_json": True, "expected_sections": expected_sections, "actual_sections": actual_sections, "missing_sections": missing_sections},
        "application_mapping": {"profile_mutated": False, "would_apply": would_apply, "normalized_sections": list(normalized.keys())},
        "metrics": {"cv_chars": len(text), "instruction_chars": len(compact_instruction), "template_chars": len(compact_template), "compact_template_chars": len(compact_template), "prompt_chars": len(prompt), "output_chars": len(compact_output)},
        "routing": {"task_type": "cv_extraction", "fallback_used": result.fallback_used, "provider_attempts": result.provider_attempts},
    }
