from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="CareerOS Intelligence Engine",
    version="0.1.0",
    description="Provider-neutral local intelligence gateway for CareerOS.",
)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "")
REQUEST_TIMEOUT = float(os.getenv("INTELLIGENCE_TIMEOUT_SECONDS", "180"))


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=120000)
    system: str | None = None
    response_schema: dict[str, Any] | None = None
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


@app.get("/health")
async def health() -> dict[str, Any]:
    model_configured = bool(OLLAMA_MODEL)
    ollama_reachable = False
    ollama_error = None
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            ollama_reachable = response.is_success
            if not response.is_success:
                ollama_error = f"HTTP {response.status_code}"
    except Exception as exc:
        ollama_error = str(exc)[:240]

    status = "ready" if model_configured and ollama_reachable else "configured" if model_configured else "unconfigured"
    return {
        "status": status,
        "provider": "ollama",
        "model_configured": model_configured,
        "model": OLLAMA_MODEL or None,
        "ollama_reachable": ollama_reachable,
        "ollama_error": ollama_error,
    }


@app.get("/v1/capabilities")
async def capabilities() -> dict[str, Any]:
    return {
        "provider": "ollama",
        "model": OLLAMA_MODEL or None,
        "capabilities": [
            "structured_output",
            "tool_orchestration_gateway",
            "document_intelligence",
            "search_reasoning",
            "opportunity_reasoning",
            "research_synthesis",
        ],
        "configured": bool(OLLAMA_MODEL),
    }


@app.post("/v1/generate")
async def generate(request: GenerateRequest) -> dict[str, Any]:
    if not OLLAMA_MODEL:
        raise HTTPException(status_code=503, detail="Local AI model is not configured yet")

    payload: dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "prompt": request.prompt,
        "stream": False,
        "options": {"temperature": request.temperature},
    }
    if request.system:
        payload["system"] = request.system
    if request.response_schema:
        payload["format"] = request.response_schema

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Local AI runtime error: {exc}") from exc

    return {
        "provider": "ollama",
        "model": OLLAMA_MODEL,
        "response": body.get("response", ""),
        "done": body.get("done", False),
        "total_duration": body.get("total_duration"),
    }
