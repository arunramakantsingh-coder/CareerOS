from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from providers import ProviderError, build_provider

app = FastAPI(
    title="CareerOS Intelligence Engine",
    version="0.2.0",
    description="Provider-neutral AI gateway for CareerOS.",
)

REQUEST_TIMEOUT = float(os.getenv("INTELLIGENCE_TIMEOUT_SECONDS", "90"))
CONFIG = {
    "AI_PROVIDER": os.getenv("AI_PROVIDER", "ollama"),
    "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
    "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", ""),
    "OPENROUTER_BASE_URL": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY", ""),
    "OPENROUTER_MODEL": os.getenv("OPENROUTER_MODEL", "openrouter/free"),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
    "GEMINI_MODEL": os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
}


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=120000)
    system: str | None = None
    response_schema: dict[str, Any] | None = None
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    provider: str | None = None
    model: str | None = None


def _provider_config(provider_name: str) -> dict[str, str]:
    config = dict(CONFIG)
    config["AI_PROVIDER"] = provider_name
    return config


def _configured_provider(name: str):
    return build_provider(_provider_config(name), REQUEST_TIMEOUT)


@app.get("/health")
async def health() -> dict[str, Any]:
    provider_name = CONFIG["AI_PROVIDER"].strip().lower()
    try:
        provider = _configured_provider(provider_name)
        provider_health = await provider.health()
    except ProviderError as exc:
        return {
            "status": "unconfigured",
            "provider": provider_name,
            "error": str(exc),
        }

    ready = provider_health.get("configured") and provider_health.get("reachable") is not False
    return {
        "status": "ready" if ready else "configured" if provider_health.get("configured") else "unconfigured",
        **provider_health,
    }


@app.get("/v1/providers")
async def providers() -> dict[str, Any]:
    result: list[dict[str, Any]] = []
    for name in ("ollama", "openrouter", "gemini"):
        try:
            provider = _configured_provider(name)
            item = await provider.health()
        except ProviderError as exc:
            item = {"provider": name, "configured": False, "error": str(exc)}
        result.append(item)

    return {
        "active_provider": CONFIG["AI_PROVIDER"].strip().lower(),
        "providers": result,
    }


@app.get("/v1/capabilities")
async def capabilities() -> dict[str, Any]:
    return {
        "provider": CONFIG["AI_PROVIDER"].strip().lower(),
        "model": (
            CONFIG["OLLAMA_MODEL"]
            if CONFIG["AI_PROVIDER"].strip().lower() == "ollama"
            else CONFIG["OPENROUTER_MODEL"]
            if CONFIG["AI_PROVIDER"].strip().lower() == "openrouter"
            else CONFIG["GEMINI_MODEL"]
        ) or None,
        "providers": ["ollama", "openrouter", "gemini"],
        "capabilities": [
            "structured_output",
            "provider_routing",
            "document_intelligence",
            "search_reasoning",
            "opportunity_reasoning",
            "research_synthesis",
        ],
    }


@app.post("/v1/generate")
async def generate(request: GenerateRequest) -> dict[str, Any]:
    provider_name = (request.provider or CONFIG["AI_PROVIDER"]).strip().lower()
    config = _provider_config(provider_name)

    if request.model:
        if provider_name == "ollama":
            config["OLLAMA_MODEL"] = request.model
        elif provider_name == "openrouter":
            config["OPENROUTER_MODEL"] = request.model
        elif provider_name == "gemini":
            config["GEMINI_MODEL"] = request.model

    try:
        provider = build_provider(config, REQUEST_TIMEOUT)
        result = await provider.generate(
            prompt=request.prompt,
            system=request.system,
            response_schema=request.response_schema,
            temperature=request.temperature,
        )
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "provider": result.provider,
        "model": result.model,
        "response": result.response,
        "done": result.done,
        "total_duration": result.total_duration,
    }
