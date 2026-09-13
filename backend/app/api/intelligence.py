from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.roles import require_developer
from app.core.security import get_current_user
from app.intelligence.contracts import IntelligenceRequest, RetrievalRequest
from app.intelligence.credential_store import decrypt_secret, encrypt_secret
from app.intelligence.engine import engine
from app.intelligence.provider_catalog import PROVIDER_CATALOG
from app.intelligence.registry import registry
from app.intelligence.retrieval import retrieve_career_knowledge
from app.models.intelligence_provider import IntelligenceProviderConfig
from app.models.user import User

router = APIRouter(prefix="/intelligence", tags=["intelligence"])
INTELLIGENCE_BASE_URL = os.getenv("INTELLIGENCE_BASE_URL", "http://intelligence:8100").rstrip("/")
TIMEOUT = float(os.getenv("INTELLIGENCE_STATUS_TIMEOUT_SECONDS", "360"))


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=120000)
    system: str | None = None
    response_schema: dict[str, Any] | None = None
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


class ProviderSaveRequest(BaseModel):
    provider: str = Field(min_length=2, max_length=50)
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    priority: int = Field(default=100, ge=1, le=1000)


class ProviderActivateRequest(BaseModel):
    provider: str = Field(min_length=2, max_length=50)


def _ensure_catalog_rows(db: Session) -> None:
    changed = False
    for name, meta in PROVIDER_CATALOG.items():
        row = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider == name).first()
        if row:
            continue
        db.add(IntelligenceProviderConfig(provider=name, label=meta["label"], category=meta["category"], model=meta["model"], base_url=meta["base_url"], configured=(name == "ollama"), active=False, priority=100, capabilities=meta["capabilities"], routing_policy={"mode": "manual", "fallback_enabled": False}))
        changed = True
    if changed:
        db.flush()
        if not db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.active.is_(True)).first():
            ollama = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider == "ollama").first()
            if ollama:
                ollama.active = True
        db.commit()


def _public_provider(row: IntelligenceProviderConfig) -> dict[str, Any]:
    return {"provider": row.provider, "label": row.label, "category": row.category, "model": row.model, "base_url": row.base_url, "configured": bool(row.configured), "active": bool(row.active), "priority": row.priority, "capabilities": row.capabilities or [], "routing_policy": row.routing_policy or {}, "api_key_present": bool(row.encrypted_api_key), "api_key_last4": row.api_key_last4 if row.encrypted_api_key else None, "last_tested_at": row.last_tested_at, "last_test_status": row.last_test_status, "last_error": row.last_error}


def _gateway_config(row: IntelligenceProviderConfig, supplied_key: str | None = None) -> dict[str, Any]:
    return {"provider": row.provider, "model": row.model, "base_url": row.base_url, "api_key": supplied_key if supplied_key is not None else decrypt_secret(row.encrypted_api_key)}


async def _call(path: str, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(f"{INTELLIGENCE_BASE_URL}{path}", json=payload or {}) if method == "POST" else await client.get(f"{INTELLIGENCE_BASE_URL}{path}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        try:
            detail = exc.response.json().get("detail", exc.response.text)
        except Exception:
            detail = exc.response.text
        raise HTTPException(status_code=exc.response.status_code if exc.response is not None else 503, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"Intelligence Engine unavailable: {exc}") from exc


@router.get("/status")
async def status(_: User = Depends(get_current_user)):
    return await _call("/health")


@router.get("/providers")
async def providers(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    _ensure_catalog_rows(db)
    rows = db.query(IntelligenceProviderConfig).order_by(IntelligenceProviderConfig.priority, IntelligenceProviderConfig.label).all()
    active = next((row.provider for row in rows if row.active), None)
    return {"active_provider": active, "providers": [_public_provider(row) for row in rows]}


def _save_row(db: Session, request: ProviderSaveRequest) -> IntelligenceProviderConfig:
    name = request.provider.strip().lower()
    if name not in PROVIDER_CATALOG:
        raise HTTPException(status_code=400, detail=f"Unsupported Intelligence provider: {name}")
    _ensure_catalog_rows(db)
    row = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider == name).first()
    if not row:
        raise HTTPException(status_code=404, detail="Provider registry entry not found")
    meta = PROVIDER_CATALOG[name]
    if request.model:
        row.model = request.model.strip()
    if request.base_url:
        row.base_url = request.base_url.rstrip("/")
    elif row.base_url is None:
        row.base_url = meta["base_url"]
    row.priority = request.priority
    if request.api_key:
        secret = request.api_key.strip()
        row.encrypted_api_key = encrypt_secret(secret)
        row.api_key_last4 = secret[-4:]
    row.configured = True if name == "ollama" else bool(row.encrypted_api_key)
    row.last_error = None
    return row


@router.post("/providers/save")
async def save_provider(request: ProviderSaveRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    row = _save_row(db, request)
    db.commit(); db.refresh(row)
    active = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.active.is_(True)).first()
    return {"provider": _public_provider(row), "active_provider": active.provider if active else None}


@router.post("/providers/configure")
async def configure_provider_legacy(request: ProviderSaveRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    """Backward-compatible Save & Activate endpoint for the older Settings UI.

    Existing saved credentials are reused when api_key is omitted. New code should
    use Save Credentials and Activate separately from Project Control.
    """
    row = _save_row(db, request)
    if row.provider != "ollama" and not row.encrypted_api_key:
        raise HTTPException(status_code=400, detail="Save provider credentials before activating this provider")
    db.query(IntelligenceProviderConfig).update({"active": False})
    row.active = True
    db.commit(); db.refresh(row)
    return {"active_provider": row.provider, "provider": _public_provider(row)}


@router.post("/providers/activate")
async def activate_provider(request: ProviderActivateRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    name = request.provider.strip().lower()
    _ensure_catalog_rows(db)
    row = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider == name).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Provider not found: {name}")
    if name != "ollama" and not row.encrypted_api_key:
        raise HTTPException(status_code=400, detail="Save provider credentials before activating this provider")
    if not row.configured:
        raise HTTPException(status_code=400, detail="Provider is not configured")
    db.query(IntelligenceProviderConfig).update({"active": False})
    row.active = True
    row.last_error = None
    db.commit()
    return {"active_provider": name, "provider": _public_provider(row)}


@router.post("/providers/test")
async def test_provider(request: ProviderSaveRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    name = request.provider.strip().lower()
    _ensure_catalog_rows(db)
    row = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider == name).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Provider not found: {name}")
    supplied_key = request.api_key.strip() if request.api_key else None
    if name != "ollama" and not supplied_key and not row.encrypted_api_key:
        raise HTTPException(status_code=400, detail="Save credentials first or provide an API key for this test")
    payload = _gateway_config(row, supplied_key)
    if request.model:
        payload["model"] = request.model.strip()
    if request.base_url:
        payload["base_url"] = request.base_url.rstrip("/")
    try:
        result = await _call("/v1/generate", method="POST", payload={"prompt": "Reply with exactly: CAREEROS_AI_TEST_OK", "temperature": 0.0, **payload})
        row.last_tested_at = datetime.now(timezone.utc).isoformat(); row.last_test_status = "passed"; row.last_error = None
        db.commit()
        return result
    except HTTPException as exc:
        row.last_tested_at = datetime.now(timezone.utc).isoformat(); row.last_test_status = "failed"; row.last_error = str(exc.detail)[:1000]
        db.commit(); raise


@router.get("/capabilities")
async def capabilities(_: User = Depends(get_current_user)):
    return {"capabilities": ["structured_output", "provider_routing", "document_intelligence", "search_reasoning", "opportunity_reasoning", "research_synthesis"], "tools": registry.list()}


@router.get("/tools")
async def tools(_: User = Depends(get_current_user)):
    return {"tools": registry.list()}


@router.post("/execute")
async def execute(request: IntelligenceRequest, _: User = Depends(get_current_user)):
    try:
        return await engine.execute(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/retrieve")
async def retrieve(request: RetrievalRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return retrieve_career_knowledge(db=db, user_id=current_user.id, query=request.query, top_k=request.top_k, filters=request.filters)


@router.post("/generate")
async def generate(request: GenerateRequest, _: User = Depends(get_current_user)):
    return await engine.generate_direct(request.model_dump(exclude_none=True))
