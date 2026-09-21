from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.core.roles import require_developer
from app.intelligence.credential_store import decrypt_secret
from app.intelligence.health_policy import DEFAULT_HEALTH_POLICY, apply_policy_to_rows, health_is_fresh, health_ttl_seconds, policy_from_rows
from app.intelligence.provider_validation import ProviderConfigurationError, validate_provider_configuration
from app.intelligence.runtime_trace import event, finish, start_trace
from app.models.intelligence_provider import IntelligenceProviderConfig
from app.models.user import User

router = APIRouter(prefix="/intelligence", tags=["intelligence-health"])
GATEWAY_BASE_URL = os.getenv("INTELLIGENCE_BASE_URL", "http://intelligence:8100").rstrip("/")
HEALTH_TIMEOUT = float(os.getenv("INTELLIGENCE_HEALTH_CHECK_TIMEOUT_SECONDS", "30"))


class HealthCheckRequest(BaseModel):
    provider: str | None = Field(default=None, min_length=2, max_length=50)
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None


class HealthPolicyRequest(BaseModel):
    enabled: bool = True
    interval_seconds: int = Field(default=900, ge=300, le=21600)
    grace_seconds: int = Field(default=60, ge=0, le=900)


def _health(row: IntelligenceProviderConfig) -> dict[str, Any]:
    return dict((row.metadata_json or {}).get("health") or {})


def _fresh(health: dict[str, Any], ttl_seconds: int) -> bool:
    if health.get("status") != "healthy" or not health.get("checked_at"):
        return False
    try:
        checked = datetime.fromisoformat(str(health["checked_at"]).replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - checked).total_seconds() <= ttl_seconds
    except ValueError:
        return False


def get_health_policy(db: Session) -> dict[str, Any]:
    rows = db.query(IntelligenceProviderConfig).order_by(IntelligenceProviderConfig.provider).all()
    return policy_from_rows(rows)


def _record_health(row: IntelligenceProviderConfig, result: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(row.metadata_json or {})
    previous = dict(metadata.get("health") or {})
    samples = list(previous.get("latency_samples") or [])[-99:]
    latency = float(result.get("latency_ms") or 0)
    samples.append(latency)
    ordered = sorted(samples)
    p50 = ordered[int((len(ordered) - 1) * 0.50)] if ordered else None
    p95 = ordered[int((len(ordered) - 1) * 0.95)] if ordered else None
    success = result.get("status") == "healthy"
    health = {"status": result.get("status", "unhealthy"), "reachable": bool(result.get("reachable")), "checked_at": datetime.now(timezone.utc).isoformat(), "last_latency_ms": round(latency, 1), "avg_latency_ms": round(sum(samples) / len(samples), 1) if samples else None, "p50_latency_ms": round(float(p50), 1) if p50 is not None else None, "p95_latency_ms": round(float(p95), 1) if p95 is not None else None, "checks": int(previous.get("checks") or 0) + 1, "successful_checks": int(previous.get("successful_checks") or 0) + (1 if success else 0), "failed_checks": int(previous.get("failed_checks") or 0) + (0 if success else 1), "consecutive_failures": 0 if success else int(previous.get("consecutive_failures") or 0) + 1, "last_error": None if success else str(result.get("error") or "Health check failed")[:500], "quota": result.get("quota") or {}, "latency_samples": samples}
    metadata["health"] = health
    row.metadata_json = metadata
    row.last_tested_at = health["checked_at"]
    row.last_test_status = "passed" if success else "failed"
    row.last_error = health["last_error"]
    return health


async def _check(row: IntelligenceProviderConfig, request: HealthCheckRequest | None = None) -> dict[str, Any]:
    supplied_key = request.api_key.strip() if request and request.api_key else None
    model = request.model.strip() if request and request.model else row.model
    base_url = request.base_url.rstrip("/") if request and request.base_url else row.base_url
    try:
        config = validate_provider_configuration(row.provider, model, base_url)
    except ProviderConfigurationError as exc:
        return {"provider": row.provider, "model": model, "status": "unhealthy", "reachable": False, "quota": {}, "error": str(exc), "latency_ms": 0}
    payload = {"provider": row.provider, "model": config["model"], "base_url": config["base_url"], "api_key": supplied_key if supplied_key is not None else decrypt_secret(row.encrypted_api_key)}
    try:
        async with httpx.AsyncClient(timeout=HEALTH_TIMEOUT) as client:
            response = await client.post(f"{GATEWAY_BASE_URL}/v1/provider-health", json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        try: detail = exc.response.json().get("detail", exc.response.text)
        except Exception: detail = exc.response.text
        return {"provider": row.provider, "model": row.model, "status": "unhealthy", "reachable": False, "error": str(detail)[:500]}
    except httpx.HTTPError as exc:
        return {"provider": row.provider, "model": row.model, "status": "unhealthy", "reachable": False, "error": str(exc)[:500]}


async def _run_configured_health_checks(db: Session, trace_id: str | None = None) -> dict[str, Any]:
    rows = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.configured.is_(True)).order_by(IntelligenceProviderConfig.priority, IntelligenceProviderConfig.label).all()
    results = []
    for row in rows:
        if trace_id: event(trace_id, "HEALTH_CHECK_STARTED", f"Checking {row.provider}", provider=row.provider, model=row.model)
        result = await _check(row)
        health = _record_health(row, result)
        results.append({"provider": row.provider, "label": row.label, "model": row.model, "health": health})
        if trace_id: event(trace_id, "HEALTH_CHECK_RESULT", f"{row.provider}: {health.get('status')}", provider=row.provider, model=row.model, latency_ms=health.get("last_latency_ms"), error=health.get("last_error"))
    db.commit()
    return {"health_ttl_seconds": health_ttl_seconds(get_health_policy(db)), "providers": results, "healthy": sum(1 for item in results if item["health"].get("status") == "healthy"), "total": len(results)}


async def _background_manual_health_check(trace_id: str, request_data: dict[str, Any]) -> None:
    db = SessionLocal()
    try:
        request = HealthCheckRequest.model_validate(request_data)
        query = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.configured.is_(True))
        if request.provider:
            query = query.filter(IntelligenceProviderConfig.provider == request.provider.strip().lower())
        rows = query.order_by(IntelligenceProviderConfig.priority, IntelligenceProviderConfig.label).all()
        if not rows:
            event(trace_id, "ROUTING_FAILED", "No configured provider matched the health-check request")
            finish(trace_id, status="failed")
            return
        event(trace_id, "HEALTH_CYCLE_STARTED", "Background provider health check started", provider=request.provider, total=len(rows))
        for row in rows:
            event(trace_id, "HEALTH_CHECK_STARTED", f"Checking {row.provider}", provider=row.provider, model=row.model)
            result = await _check(row, request if request.provider and row.provider == request.provider.strip().lower() else None)
            health = _record_health(row, result)
            event(
                trace_id,
                "HEALTH_CHECK_RESULT",
                f"{row.provider}: {health.get('status')}",
                provider=row.provider,
                model=row.model,
                latency_ms=health.get("last_latency_ms"),
                error=health.get("last_error"),
            )
            db.commit()
        healthy = sum(
            1 for row in rows
            if (_health(row) or {}).get("status") == "healthy"
        )
        event(trace_id, "HEALTH_CYCLE_COMPLETED", "Background provider health check completed", healthy=healthy, total=len(rows))
        finish(trace_id, status="completed", total_latency_ms=sum(float((_health(row) or {}).get("last_latency_ms") or 0) for row in rows))
    except Exception as exc:
        db.rollback()
        event(trace_id, "GENERATION_FAILED", "Background provider health check failed", error=str(exc)[:500])
        finish(trace_id, status="failed")
    finally:
        db.close()


async def _background_provider_connection_test(trace_id: str, request_data: dict[str, Any]) -> None:
    db = SessionLocal()
    started = datetime.now(timezone.utc)
    try:
        request = HealthCheckRequest.model_validate(request_data)
        name = (request.provider or "").strip().lower()
        row = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider == name).first()
        if not row:
            event(trace_id, "ROUTING_FAILED", f"Provider not found: {name}")
            finish(trace_id, status="failed")
            return
        event(trace_id, "TASK_IDENTIFIED", f"Connection test requested for {name}", provider=name, model=request.model or row.model)
        supplied_key = request.api_key.strip() if request.api_key else None
        if name != "ollama" and not supplied_key and not row.encrypted_api_key:
            raise RuntimeError("Save credentials first or provide an API key for this test")
        model = request.model.strip() if request.model else row.model
        base_url = request.base_url.rstrip("/") if request.base_url else row.base_url
        config = validate_provider_configuration(name, model, base_url)
        event(trace_id, "CONFIGURATION_VALIDATED", f"Configuration validated for {name}", provider=name, model=config["model"])
        payload = {
            "provider": name,
            "model": config["model"],
            "base_url": config["base_url"],
            "api_key": supplied_key if supplied_key is not None else decrypt_secret(row.encrypted_api_key),
            "prompt": "Reply with exactly: CAREEROS_AI_TEST_OK",
            "temperature": 0.0,
            "stream": False,
            "trace_id": trace_id,
        }
        event(trace_id, "CONNECTION_CHECK_STARTED", f"Sending connection test to {name}", provider=name, model=config["model"])
        async with httpx.AsyncClient(timeout=HEALTH_TIMEOUT) as client:
            response = await client.post(f"{GATEWAY_BASE_URL}/v1/generate", json=payload)
            response.raise_for_status()
            body = response.json()
        output = str(body.get("response") or "")
        update(trace_id, selected_provider=name, selected_model=config["model"], output_chars=len(output), output_preview=output[-2000:])
        event(trace_id, "PROVIDER_RESPONSE_RECEIVED", f"Connection test response received from {name}", provider=name, model=config["model"], chars=len(output))
        if not output.strip():
            raise RuntimeError(f"{name} returned an empty AI response")
        row.model = config["model"]
        row.base_url = config["base_url"] or row.base_url
        row.last_tested_at = datetime.now(timezone.utc).isoformat()
        row.last_test_status = "passed"
        row.last_error = None
        db.commit()
        event(trace_id, "CONNECTION_CHECK_COMPLETED", f"Connection test passed for {name}", provider=name, model=config["model"], latency_ms=(datetime.now(timezone.utc) - started).total_seconds() * 1000)
        finish(trace_id, status="completed", final_provider=name, total_latency_ms=(datetime.now(timezone.utc) - started).total_seconds() * 1000)
    except Exception as exc:
        db.rollback()
        try:
            name = (request_data.get("provider") or "").strip().lower()
            row = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider == name).first()
            if row:
                row.last_tested_at = datetime.now(timezone.utc).isoformat()
                row.last_test_status = "failed"
                row.last_error = str(exc)[:1000]
                db.commit()
        except Exception:
            db.rollback()
        event(trace_id, "CONNECTION_CHECK_FAILED", "Provider connection test failed", provider=request_data.get("provider"), error=str(exc)[:500])
        finish(trace_id, status="failed", total_latency_ms=(datetime.now(timezone.utc) - started).total_seconds() * 1000)
    finally:
        db.close()


@router.post("/providers/health-check/start")
async def start_provider_health_check(request: HealthCheckRequest, _: User = Depends(require_developer)):
    trace_id = start_trace("provider_health_check", [])
    event(trace_id, "HEALTH_CYCLE_QUEUED", "Provider health check queued", provider=request.provider)
    asyncio.create_task(_background_manual_health_check(trace_id, request.model_dump()))
    return {"trace_id": trace_id, "status": "running"}


@router.post("/providers/test/start")
async def start_provider_connection_test(request: HealthCheckRequest, _: User = Depends(require_developer)):
    if not request.provider:
        raise HTTPException(status_code=400, detail="Provider is required for a connection test")
    trace_id = start_trace("provider_connection_test", [], context={"provider": request.provider})
    event(trace_id, "CONNECTION_CHECK_QUEUED", "Provider connection test queued", provider=request.provider, model=request.model)
    asyncio.create_task(_background_provider_connection_test(trace_id, request.model_dump()))
    return {"trace_id": trace_id, "status": "running"}


@router.get("/providers/health-policy")
async def provider_health_policy(db: Session = Depends(get_db), _: User = Depends(require_developer)):
    policy = get_health_policy(db)
    return {**policy, "health_ttl_seconds": health_ttl_seconds(policy), "min_interval_seconds": 300, "max_interval_seconds": 21600}


@router.post("/providers/health-policy")
async def update_provider_health_policy(request: HealthPolicyRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    rows = db.query(IntelligenceProviderConfig).all()
    if not rows: raise HTTPException(status_code=404, detail="Provider registry is empty")
    policy = apply_policy_to_rows(rows, request.model_dump())
    db.commit()
    return {**policy, "health_ttl_seconds": health_ttl_seconds(policy)}


@router.get("/providers/health")
async def provider_health(db: Session = Depends(get_db), _: User = Depends(require_developer)):
    rows = db.query(IntelligenceProviderConfig).order_by(IntelligenceProviderConfig.priority, IntelligenceProviderConfig.label).all()
    policy = policy_from_rows(rows); ttl = health_ttl_seconds(policy)
    return {"health_ttl_seconds": ttl, "health_policy": policy, "providers": [{"provider": row.provider, "label": row.label, "configured": bool(row.configured), "active": bool(row.active), "model": row.model, "priority": row.priority, "health": _health(row), "health_fresh": _fresh(_health(row), ttl)} for row in rows]}


@router.post("/providers/health-check")
async def run_provider_health_check(request: HealthCheckRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    query = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.configured.is_(True))
    if request.provider: query = query.filter(IntelligenceProviderConfig.provider == request.provider.strip().lower())
    rows = query.order_by(IntelligenceProviderConfig.priority, IntelligenceProviderConfig.label).all()
    if not rows: raise HTTPException(status_code=404, detail="No configured Intelligence providers matched the health-check request")
    trace_id = start_trace("provider_health_check", [])
    event(trace_id, "HEALTH_CYCLE_STARTED", "Manual provider health check started", provider=request.provider)
    results = []
    for row in rows:
        event(trace_id, "HEALTH_CHECK_STARTED", f"Checking {row.provider}", provider=row.provider, model=row.model)
        result = await _check(row, request if request.provider and row.provider == request.provider.strip().lower() else None)
        health = _record_health(row, result)
        results.append({"provider": row.provider, "label": row.label, "model": row.model, "health": health})
        event(trace_id, "HEALTH_CHECK_RESULT", f"{row.provider}: {health.get('status')}", provider=row.provider, model=row.model, latency_ms=health.get("last_latency_ms"), error=health.get("last_error"))
    db.commit()
    event(trace_id, "HEALTH_CYCLE_COMPLETED", "Manual provider health check completed", healthy=sum(1 for item in results if item["health"].get("status") == "healthy"), total=len(results))
    finish(trace_id, status="completed", total_latency_ms=sum(float(item["health"].get("last_latency_ms") or 0) for item in results))
    policy = get_health_policy(db)
    return {"trace_id": trace_id, "health_ttl_seconds": health_ttl_seconds(policy), "health_policy": policy, "providers": results}
