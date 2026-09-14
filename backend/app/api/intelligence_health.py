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
from app.intelligence.credential_store import decrypt_secret
from app.intelligence.health_policy import (
    DEFAULT_HEALTH_POLICY,
    apply_policy_to_rows,
    health_is_fresh,
    health_ttl_seconds,
    policy_from_rows,
)
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
    health = {
        "status": result.get("status", "unhealthy"),
        "reachable": bool(result.get("reachable")),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "last_latency_ms": round(latency, 1),
        "avg_latency_ms": round(sum(samples) / len(samples), 1) if samples else None,
        "p50_latency_ms": round(float(p50), 1) if p50 is not None else None,
        "p95_latency_ms": round(float(p95), 1) if p95 is not None else None,
        "checks": int(previous.get("checks") or 0) + 1,
        "successful_checks": int(previous.get("successful_checks") or 0) + (1 if success else 0),
        "failed_checks": int(previous.get("failed_checks") or 0) + (0 if success else 1),
        "consecutive_failures": 0 if success else int(previous.get("consecutive_failures") or 0) + 1,
        "last_error": None if success else str(result.get("error") or "Health check failed")[:500],
        "quota": result.get("quota") or {},
        "latency_samples": samples,
    }
    metadata["health"] = health
    row.metadata_json = metadata
    row.last_tested_at = health["checked_at"]
    row.last_test_status = "passed" if success else "failed"
    row.last_error = health["last_error"]
    return health


async def _check(row: IntelligenceProviderConfig, request: HealthCheckRequest | None = None) -> dict[str, Any]:
    supplied_key = request.api_key.strip() if request and request.api_key else None
    payload = {
        "provider": row.provider,
        "model": (request.model.strip() if request and request.model else row.model),
        "base_url": (request.base_url.rstrip("/") if request and request.base_url else row.base_url),
        "api_key": supplied_key if supplied_key is not None else decrypt_secret(row.encrypted_api_key),
    }
    try:
        async with httpx.AsyncClient(timeout=HEALTH_TIMEOUT) as client:
            response = await client.post(f"{GATEWAY_BASE_URL}/v1/provider-health", json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        try:
            detail = exc.response.json().get("detail", exc.response.text)
        except Exception:
            detail = exc.response.text
        return {"provider": row.provider, "model": row.model, "status": "unhealthy", "reachable": False, "error": str(detail)[:500]}
    except httpx.HTTPError as exc:
        return {"provider": row.provider, "model": row.model, "status": "unhealthy", "reachable": False, "error": str(exc)[:500]}


async def _run_configured_health_checks(db: Session) -> dict[str, Any]:
    rows = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.configured.is_(True)).order_by(IntelligenceProviderConfig.priority, IntelligenceProviderConfig.label).all()
    results = []
    for row in rows:
        result = await _check(row)
        health = _record_health(row, result)
        results.append({"provider": row.provider, "label": row.label, "model": row.model, "health": health})
    db.commit()
    return {
        "health_ttl_seconds": health_ttl_seconds(get_health_policy(db)),
        "providers": results,
        "healthy": sum(1 for item in results if item["health"].get("status") == "healthy"),
        "total": len(results),
    }


@router.get("/providers/health-policy")
async def provider_health_policy(db: Session = Depends(get_db), _: User = Depends(require_developer)):
    policy = get_health_policy(db)
    return {
        **policy,
        "health_ttl_seconds": health_ttl_seconds(policy),
        "min_interval_seconds": 300,
        "max_interval_seconds": 21600,
    }


@router.post("/providers/health-policy")
async def update_provider_health_policy(request: HealthPolicyRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    rows = db.query(IntelligenceProviderConfig).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Provider registry is empty")
    policy = apply_policy_to_rows(rows, request.model_dump())
    db.commit()
    return {**policy, "health_ttl_seconds": health_ttl_seconds(policy)}


@router.get("/providers/health")
async def provider_health(db: Session = Depends(get_db), _: User = Depends(require_developer)):
    rows = db.query(IntelligenceProviderConfig).order_by(IntelligenceProviderConfig.priority, IntelligenceProviderConfig.label).all()
    policy = policy_from_rows(rows)
    ttl = health_ttl_seconds(policy)
    return {
        "health_ttl_seconds": ttl,
        "health_policy": policy,
        "providers": [
            {
                "provider": row.provider,
                "label": row.label,
                "configured": bool(row.configured),
                "active": bool(row.active),
                "model": row.model,
                "priority": row.priority,
                "health": _health(row),
                "health_fresh": _fresh(_health(row), ttl),
            }
            for row in rows
        ],
    }


@router.post("/providers/health-check")
async def run_provider_health_check(request: HealthCheckRequest, db: Session = Depends(get_db), _: User = Depends(require_developer)):
    query = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.configured.is_(True))
    if request.provider:
        name = request.provider.strip().lower()
        query = query.filter(IntelligenceProviderConfig.provider == name)
    rows = query.order_by(IntelligenceProviderConfig.priority, IntelligenceProviderConfig.label).all()
    if not rows:
        raise HTTPException(status_code=404, detail="No configured Intelligence providers matched the health-check request")

    results = []
    for row in rows:
        result = await _check(row, request if request.provider and row.provider == request.provider.strip().lower() else None)
        health = _record_health(row, result)
        results.append({"provider": row.provider, "label": row.label, "model": row.model, "health": health})
    db.commit()
    policy = get_health_policy(db)
    return {"health_ttl_seconds": health_ttl_seconds(policy), "health_policy": policy, "providers": results}
