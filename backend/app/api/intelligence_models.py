from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.roles import require_developer
from app.intelligence.provider_catalog import PROVIDER_CATALOG
from app.models.intelligence_provider import IntelligenceProviderConfig
from app.models.user import User

router = APIRouter(prefix="/intelligence/providers", tags=["intelligence-provider-models"])


@router.get("/models")
async def provider_models(
    provider: str = Query(default="ollama", min_length=2, max_length=50),
    db: Session = Depends(get_db),
    _: User = Depends(require_developer),
) -> dict[str, Any]:
    name = provider.strip().lower()
    if name not in PROVIDER_CATALOG:
        raise HTTPException(status_code=400, detail=f"Unsupported Intelligence provider: {name}")

    row = db.query(IntelligenceProviderConfig).filter(IntelligenceProviderConfig.provider == name).first()
    configured_model = (row.model if row else None) or PROVIDER_CATALOG[name].get("model")

    if name != "ollama":
        models: list[dict[str, Any]] = []
        if configured_model:
            models.append({"name": configured_model, "source": "configured"})
        catalog_model = PROVIDER_CATALOG[name].get("model")
        if catalog_model and catalog_model != configured_model:
            models.append({"name": catalog_model, "source": "catalog_default"})
        return {"provider": name, "source": "configured", "models": models, "selected_model": configured_model}

    base_url = (row.base_url if row else None) or os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    base_url = base_url.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}/api/tags")
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Unable to query Ollama model catalog: HTTP {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"Unable to reach Ollama model catalog: {exc}") from exc

    discovered: list[dict[str, Any]] = []
    for item in body.get("models") or []:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        details = item.get("details") or {}
        discovered.append({
            "name": item["name"],
            "source": "ollama_local",
            "size": item.get("size"),
            "modified_at": item.get("modified_at"),
            "parameter_size": details.get("parameter_size"),
            "quantization_level": details.get("quantization_level"),
            "family": details.get("family"),
        })

    names = {item["name"] for item in discovered}
    if configured_model and configured_model not in names:
        discovered.insert(0, {"name": configured_model, "source": "configured_not_detected"})

    return {
        "provider": name,
        "source": "ollama_local",
        "base_url": base_url,
        "models": discovered,
        "selected_model": configured_model if configured_model in {item["name"] for item in discovered} else (discovered[0]["name"] if discovered else None),
    }
