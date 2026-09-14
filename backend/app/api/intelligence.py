from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.roles import require_developer
from app.core.security import get_current_user
from app.intelligence.contracts import IntelligenceRequest, RetrievalRequest
from app.intelligence.credential_store import decrypt_secret, encrypt_secret
from app.intelligence.engine import engine
from app.intelligence.engine_runtime import TASK_REQUIREMENTS, routed_engine
from app.intelligence.health_policy import health_is_fresh, health_ttl_seconds, policy_from_rows
from app.intelligence.provider_catalog import PROVIDER_CATALOG
from app.intelligence.provider_validation import ProviderConfigurationError, validate_provider_configuration
from app.intelligence.registry import registry
from app.intelligence.retrieval import retrieve_career_knowledge
from app.intelligence.runtime_trace import get_trace, list_traces
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


class RoutingPolicyRequest(BaseModel):
    provider: str = Field(min_length=2, max_length=50)
    fallback_enabled: bool = True
    daily_request_limit: int | None = Field(default=None, ge=1, le=1000000)


def _lifecycle(row: IntelligenceProviderConfig) -> str:
    metadata = row.metadata_json or {}
    stored = str(metadata.get("lifecycle_state") or "").lower()
    if stored in {"not_configured", "configured", "active", "deactivated"}:
        return stored
    return "active" if row.active else "configured" if row.configured else "not_configured"


def _set_lifecycle(row: IntelligenceProviderConfig, state: str) -> None:
    metadata = dict(row.metadata_json or {})
    metadata["lifecycle_state"] = state
    row.metadata_json = metadata


def _ensure_catalog_rows(db: Session) -> None:
    changed = False
    env_provider = os.getenv("AI_PROVIDER", "ollama").strip().lower()
    env_keys = {"openrouter": os.getenv("OPENROUTER_API_KEY", ""), "gemini": os.getenv("GEMINI_API_KEY", "")}
    for name, meta in PROVIDER_CATALOG.items():
        row = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider == name).first()
        if row:
            # Existing development databases may still contain the old dynamic
            # openrouter/free selector. Migrate that value to the pinned catalog model
            # so fallback remains deterministic without requiring a DB reset/migration.
            if name == "openrouter" and str(row.model or "").strip().lower() in {"openrouter/free", "openrouter/free:auto", "free", ""} and meta.get("model"):
                row.model = meta["model"]
                changed = True
            if name == "openrouter" and not row.base_url and meta.get("base_url"):
                row.base_url = meta["base_url"]
                changed = True
            continue
        env_key = env_keys.get(name, "")
        db.add(IntelligenceProviderConfig(provider=name, label=meta["label"], category=meta["category"], model=meta["model"], base_url=meta["base_url"], encrypted_api_key=encrypt_secret(env_key) if env_key else None, api_key_last4=env_key[-4:] if env_key else None, configured=(name == "ollama" or bool(env_key)), active=False, priority=100, capabilities=meta["capabilities"], routing_policy={"mode": "health_gated_dynamic", "fallback_enabled": True, "daily_request_limit": None, "operator_primary": False}, metadata_json={"lifecycle_state": "configured" if name == "ollama" or bool(env_key) else "not_configured"}))
        changed = True
    if changed:
        db.flush()
        preferred = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider == env_provider, IntelligenceProviderConfig.configured.is_(True)).first()
        if not preferred:
            preferred = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider == "ollama").first()
        if preferred and not db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.active.is_(True)).first():
            preferred.active = True
            _set_lifecycle(preferred, "active")
            preferred.routing_policy = {**(preferred.routing_policy or {}), "operator_primary": True}
        db.commit()


def _configuration_error(row: IntelligenceProviderConfig) -> str | None:
    try:
        validate_provider_configuration(row.provider, row.model, row.base_url)
    except ProviderConfigurationError as exc:
        return str(exc)
    if row.configured and row.provider != "ollama" and not row.encrypted_api_key:
        return "API credential is not configured"
    return None


def _public_provider(row: IntelligenceProviderConfig) -> dict[str, Any]:
    metadata = row.metadata_json or {}
    telemetry = metadata.get("telemetry") or {}
    policy = row.routing_policy or {}
    health = metadata.get("health") or {}
    lifecycle = _lifecycle(row)
    return {"provider": row.provider, "label": row.label, "category": row.category, "model": row.model, "base_url": row.base_url, "configured": bool(row.configured), "active": bool(row.active), "control_state": lifecycle, "deactivated": lifecycle == "deactivated", "priority": row.priority, "capabilities": row.capabilities or [], "routing_policy": policy, "api_key_present": bool(row.encrypted_api_key), "api_key_last4": row.api_key_last4 if row.encrypted_api_key else None, "last_tested_at": row.last_tested_at, "last_test_status": row.last_test_status, "last_error": row.last_error, "configuration_valid": _configuration_error(row) is None, "configuration_error": _configuration_error(row), "telemetry": telemetry, "health": health}


def _gateway_config(row: IntelligenceProviderConfig, supplied_key: str | None = None) -> dict[str, Any]:
    config = validate_provider_configuration(row.provider, row.model, row.base_url)
    return {"provider": row.provider, "model": config["model"], "base_url": config["base_url"], "api_key": supplied_key if supplied_key is not None else decrypt_secret(row.encrypted_api_key)}


def _health_is_fresh(row: IntelligenceProviderConfig, db: Session) -> bool:
    rows = db.query(IntelligenceProviderConfig).all()
    return health_is_fresh(row, health_ttl_seconds(policy_from_rows(rows)))


def _health_rank_key(row: IntelligenceProviderConfig) -> tuple[float, float, float, float, int, int, str]:
    health = (row.metadata_json or {}).get("health") or {}
    checks = int(health.get("checks") or 0)
    successful = int(health.get("successful_checks") or 0)
    reliability = successful / checks if checks else 0.0
    recent_failures = int(health.get("consecutive_failures") or 0)
    p95 = float(health.get("p95_latency_ms") or 999999.0)
    avg = float(health.get("avg_latency_ms") or 999999.0)
    operator_primary = bool((row.routing_policy or {}).get("operator_primary"))
    return (-reliability, recent_failures, p95, avg, 0 if operator_primary else 1, int(row.priority), row.label)


def _primary_active(rows: list[IntelligenceProviderConfig], db: Session) -> IntelligenceProviderConfig | None:
    eligible = [row for row in rows if row.active and row.configured and _configuration_error(row) is None and _health_is_fresh(row, db)]
    return sorted(eligible, key=_health_rank_key)[0] if eligible else None


def _capabilities(row: IntelligenceProviderConfig) -> set[str]:
    return set(row.capabilities or []) | set((PROVIDER_CATALOG.get(row.provider) or {}).get("capabilities") or [])


async def _call(path: str, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(f"{INTELLIGENCE_BASE_URL}{path}", json=payload or {}) if method == "POST" else await client.get(f"{INTELLIGENCE_BASE_URL}{path}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        try: detail = exc.response.json().get("detail", exc.response.text)
        except Exception: detail = exc.response.text
        raise HTTPException(status_code=exc.response.status_code if exc.response is not None else 503, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"Intelligence Engine unavailable: {exc}") from exc


@router.get("/status")
async def status(_: User = Depends(get_current_user)): return await _call("/health")


@router.get("/providers")
async def providers(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    _ensure_catalog_rows(db)
    rows = db.query(IntelligenceProviderConfig).order_by(IntelligenceProviderConfig.priority, IntelligenceProviderConfig.label).all()
    active = _primary_active(rows, db)
    return {"active_provider": active.provider if active else None, "active_providers": [row.provider for row in rows if row.active], "providers": [_public_provider(row) for row in rows]}


@router.get("/observability")
async def observability(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    _ensure_catalog_rows(db)
    rows = db.query(IntelligenceProviderConfig).order_by(IntelligenceProviderConfig.priority, IntelligenceProviderConfig.label).all()
    configured = [row for row in rows if row.configured]
    active = [row for row in configured if row.active]
    healthy = [row for row in active if _health_is_fresh(row, db)]
    total_requests = total_tokens = total_failures = total_fallbacks = 0
    for row in rows:
        telemetry = (row.metadata_json or {}).get("telemetry") or {}
        total_requests += int(telemetry.get("requests") or 0); total_tokens += int(telemetry.get("total_tokens") or 0); total_failures += int(telemetry.get("failed_requests") or 0); total_fallbacks += int(telemetry.get("fallback_requests") or 0)
    primary = _primary_active(rows, db); policy = policy_from_rows(rows)
    routing = {"strategy": "hard gates → task compatibility → reliability → recent failures → p95 latency → average latency → operator preference → manual priority", "health_ttl_seconds": health_ttl_seconds(policy), "active_provider": primary.provider if primary else None, "active_providers": [row.provider for row in sorted(active, key=_health_rank_key)], "active_provider_healthy": bool(primary and _health_is_fresh(primary, db)), "fallback_enabled": bool((primary.routing_policy or {}).get("fallback_enabled", True)) if primary else False, "configured_provider_order": [row.provider for row in sorted(configured, key=lambda x: (x.priority, x.label))], "active_provider_order": [row.provider for row in sorted(active, key=_health_rank_key)], "healthy_provider_order": [row.provider for row in sorted(healthy, key=_health_rank_key)], "tasks": TASK_REQUIREMENTS}
    return {"routing": routing, "usage": {"requests": total_requests, "total_tokens": total_tokens, "failed_requests": total_failures, "fallback_requests": total_fallbacks}, "providers": [_public_provider(row) for row in rows]}


@router.get("/routing/preview")
async def routing_preview(task_type: str = Query(default="profile_reconciliation", min_length=2, max_length=80), db: Session = Depends(get_db), _: User = Depends(require_developer)):
    _ensure_catalog_rows(db); rows = db.query(IntelligenceProviderConfig).all(); task_type = task_type.strip().lower(); requirements = TASK_REQUIREMENTS.get(task_type, TASK_REQUIREMENTS["general"]); policy = policy_from_rows(rows); ttl = health_ttl_seconds(policy); eligible=[]; excluded=[]
    for row in rows:
        reason=None; capabilities=self._capabilities(row) if False else _capabilities(row)
        if not row.configured: reason="not_configured"
        elif not row.active: reason=_lifecycle(row)
        elif _configuration_error(row): reason=f"invalid_configuration: {_configuration_error(row)}"
        elif not health_is_fresh(row, ttl): reason="stale_or_unhealthy_health"
        elif not all(cap in capabilities for cap in requirements): reason=f"missing_capabilities: {', '.join(cap for cap in requirements if cap not in capabilities)}"
        elif not routed_engine._within_daily_limit(row): reason="daily_request_limit"
        elif not routed_engine._quota_available(row): reason="provider_quota_exhausted"
        if reason: excluded.append({"provider": row.provider, "model": row.model, "reason": reason})
        else: eligible.append(row)
    ranked=sorted(eligible,key=_health_rank_key)
    return {"task_type":task_type,"required_capabilities":requirements,"health_ttl_seconds":ttl,"candidates":[{"provider":r.provider,"model":r.model,"rank":i+1,"reason":"eligible"} for i,r in enumerate(ranked)],"excluded_candidates":excluded,"selected_provider":ranked[0].provider if ranked else None,"selected_model":ranked[0].model if ranked else None,"ranking_reason":"reliability → recent failures → p95 latency → average latency → operator preference → manual priority"}


@router.get("/runtime-traces")
async def runtime_traces(limit: int = Query(default=25, ge=1, le=100), _: User = Depends(require_developer)): return {"traces": list_traces(limit)}


@router.get("/runtime-traces/{trace_id}")
async def runtime_trace(trace_id: str, _: User = Depends(require_developer)):
    trace=get_trace(trace_id)
    if not trace: raise HTTPException(status_code=404, detail="Runtime trace not found")
    return trace


@router.post("/routing/policy")
async def routing_policy(request: RoutingPolicyRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    _ensure_catalog_rows(db); row=db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider==request.provider.strip().lower()).first()
    if not row: raise HTTPException(status_code=404, detail=f"Provider not found: {request.provider}")
    policy=dict(row.routing_policy or {}); policy.update({"mode":"health_gated_dynamic","fallback_enabled":request.fallback_enabled,"daily_request_limit":request.daily_request_limit}); row.routing_policy=policy; db.commit(); return {"provider":_public_provider(row)}


def _save_row(db: Session, request: ProviderSaveRequest) -> IntelligenceProviderConfig:
    name=request.provider.strip().lower()
    if name not in PROVIDER_CATALOG: raise HTTPException(status_code=400, detail=f"Unsupported Intelligence provider: {name}")
    _ensure_catalog_rows(db); row=db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider==name).first()
    if not row: raise HTTPException(status_code=404, detail="Provider registry entry not found")
    meta=PROVIDER_CATALOG[name]; model=request.model.strip() if request.model else row.model or meta["model"]; base_url=request.base_url.rstrip("/") if request.base_url else row.base_url or meta["base_url"]
    try: validated=validate_provider_configuration(name,model,base_url)
    except ProviderConfigurationError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    row.model=validated["model"]; row.base_url=validated["base_url"]; row.priority=request.priority
    if request.api_key:
        secret=request.api_key.strip(); row.encrypted_api_key=encrypt_secret(secret); row.api_key_last4=secret[-4:]
    row.configured=True if name=="ollama" else bool(row.encrypted_api_key); _set_lifecycle(row,"active" if row.active else "configured"); row.last_error=None
    policy=dict(row.routing_policy or {}); policy.setdefault("mode","health_gated_dynamic"); policy.setdefault("fallback_enabled",True); policy.setdefault("daily_request_limit",None); policy.setdefault("operator_primary",False); row.routing_policy=policy
    return row


@router.post("/providers/save")
async def save_provider(request: ProviderSaveRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    row=_save_row(db,request); db.commit(); db.refresh(row); active=_primary_active(db.query(IntelligenceProviderConfig).all(),db); return {"provider":_public_provider(row),"active_provider":active.provider if active else None}


@router.post("/providers/configure")
async def configure_provider_legacy(request: ProviderSaveRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    row=_save_row(db,request)
    if row.provider!="ollama" and not row.encrypted_api_key: raise HTTPException(status_code=400, detail="Save provider credentials before activating this provider")
    if not _health_is_fresh(row,db): raise HTTPException(status_code=409, detail=f"Run a successful provider health check before activating {row.provider}")
    for other in db.query(IntelligenceProviderConfig).all(): other.routing_policy={**(other.routing_policy or {}),"operator_primary":other.provider==row.provider}
    row.active=True; _set_lifecycle(row,"active"); db.commit(); db.refresh(row); return {"active_provider":row.provider,"provider":_public_provider(row)}


@router.post("/providers/activate")
async def activate_provider(request: ProviderActivateRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    name=request.provider.strip().lower(); _ensure_catalog_rows(db); row=db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider==name).first()
    if not row: raise HTTPException(status_code=404, detail=f"Provider not found: {name}")
    if name!="ollama" and not row.encrypted_api_key: raise HTTPException(status_code=400, detail="Save provider credentials before activating this provider")
    if not row.configured: raise HTTPException(status_code=400, detail="Provider is not configured")
    try: validate_provider_configuration(name,row.model,row.base_url)
    except ProviderConfigurationError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not _health_is_fresh(row,db): raise HTTPException(status_code=409, detail=f"Run a successful provider health check before activating {name}")
    for other in db.query(IntelligenceProviderConfig).all(): other.routing_policy={**(other.routing_policy or {}),"operator_primary":other.provider==name}
    row.active=True; _set_lifecycle(row,"active"); row.last_error=None; db.commit(); active_rows=db.query(IntelligenceProviderConfig).all(); primary=_primary_active(active_rows,db); return {"active_provider":primary.provider if primary else name,"active_providers":[item.provider for item in active_rows if item.active],"provider":_public_provider(row)}


@router.post("/providers/deactivate")
async def deactivate_provider(request: ProviderActivateRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    name=request.provider.strip().lower(); _ensure_catalog_rows(db); row=db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider==name).first()
    if not row: raise HTTPException(status_code=404, detail=f"Provider not found: {name}")
    row.active=False; _set_lifecycle(row,"deactivated" if row.configured else "not_configured"); row.routing_policy={**(row.routing_policy or {}),"operator_primary":False}; db.commit(); db.refresh(row); active_rows=db.query(IntelligenceProviderConfig).all(); primary=_primary_active(active_rows,db); return {"active_provider":primary.provider if primary else None,"active_providers":[item.provider for item in active_rows if item.active],"provider":_public_provider(row)}


@router.post("/providers/test")
async def test_provider(request: ProviderSaveRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    name=request.provider.strip().lower(); _ensure_catalog_rows(db); row=db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider==name).first()
    if not row: raise HTTPException(status_code=404, detail=f"Provider not found: {name}")
    supplied_key=request.api_key.strip() if request.api_key else None
    if name!="ollama" and not supplied_key and not row.encrypted_api_key: raise HTTPException(status_code=400, detail="Save credentials first or provide an API key for this test")
    try:
        payload=_gateway_config(row,supplied_key)
        if request.model or request.base_url: payload.update(validate_provider_configuration(name,request.model or row.model,request.base_url if request.base_url is not None else row.base_url))
        result=await _call("/v1/generate",method="POST",payload={"prompt":"Reply with exactly: CAREEROS_AI_TEST_OK","temperature":0.0,**payload})
        row.last_tested_at=datetime.now(timezone.utc).isoformat(); row.last_test_status="passed"; row.last_error=None; db.commit(); return result
    except ProviderConfigurationError as exc:
        row.last_tested_at=datetime.now(timezone.utc).isoformat(); row.last_test_status="failed"; row.last_error=str(exc); db.commit(); raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException as exc:
        row.last_tested_at=datetime.now(timezone.utc).isoformat(); row.last_test_status="failed"; row.last_error=str(exc.detail)[:1000]; db.commit(); raise


@router.get("/capabilities")
async def capabilities(_: User = Depends(get_current_user)): return {"capabilities":["structured_output","provider_routing","document_intelligence","search_reasoning","opportunity_reasoning","research_synthesis","fallback_routing","usage_policy","telemetry","provider_health"],"tools":registry.list()}


@router.get("/tools")
async def tools(_: User = Depends(get_current_user)): return {"tools":registry.list()}


@router.post("/execute")
async def execute(request: IntelligenceRequest, _: User = Depends(get_current_user)):
    try: return await engine.execute(request)
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/retrieve")
async def retrieve(request: RetrievalRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return retrieve_career_knowledge(db=db,user_id=current_user.id,query=request.query,top_k=request.top_k,filters=request.filters)


@router.post("/generate")
async def generate(request: GenerateRequest, _: User = Depends(get_current_user)): return await engine.generate_direct(request.model_dump(exclude_none=True))
