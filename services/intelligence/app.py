from __future__ import annotations

import json
import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from health import check_provider_health
from providers import OllamaProvider, ProviderError, build_provider
from streaming import normalize_ollama_chunk

app = FastAPI(title="CareerOS Intelligence Engine", version="0.3.0", description="Provider-neutral global AI gateway for CareerOS.")
REQUEST_TIMEOUT = float(os.getenv("INTELLIGENCE_TIMEOUT_SECONDS", "300"))
CONFIG = {
    "AI_PROVIDER": os.getenv("AI_PROVIDER", "ollama"),
    "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
    "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "gemma3:4b"),
}
SUPPORTED_PROVIDERS = ["ollama", "openrouter", "openai", "gemini", "anthropic", "mistral", "xai", "groq", "deepseek", "ainterceptor"]


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=120000)
    system: str | None = None
    response_schema: dict[str, Any] | None = None
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    provider: str | None = None
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    think: bool | str | None = None


class ConfigureRequest(BaseModel):
    provider: str = Field(min_length=2, max_length=50)
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None


class ProviderHealthRequest(BaseModel):
    provider: str = Field(min_length=2, max_length=50)
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None


def _provider_config(request: GenerateRequest | None = None, provider_name: str | None = None) -> dict[str, str]:
    config = dict(CONFIG)
    config["AI_PROVIDER"] = (provider_name or request.provider if request and request.provider else CONFIG["AI_PROVIDER"]).strip().lower()
    if request:
        if request.model:
            config["model"] = request.model
        if request.api_key:
            config["api_key"] = request.api_key
        if request.base_url:
            config["base_url"] = request.base_url.rstrip("/")
    return config


def _configured_provider(name: str):
    return build_provider(_provider_config(provider_name=name), REQUEST_TIMEOUT)


@app.get("/health")
async def health() -> dict[str, Any]:
    provider_name = CONFIG["AI_PROVIDER"].strip().lower()
    try:
        provider_health = await _configured_provider(provider_name).health()
    except ProviderError as exc:
        return {"status": "unconfigured", "provider": provider_name, "error": str(exc)}
    ready = provider_health.get("configured") and provider_health.get("reachable") is not False
    return {"status": "ready" if ready else "configured" if provider_health.get("configured") else "unconfigured", **provider_health}


@app.get("/v1/providers")
async def providers() -> dict[str, Any]:
    result: list[dict[str, Any]] = []
    for name in SUPPORTED_PROVIDERS:
        try:
            item = await _configured_provider(name).health()
        except ProviderError as exc:
            item = {"provider": name, "configured": False, "model": None, "reachable": False, "error": str(exc)}
        result.append(item)
    return {"active_provider": CONFIG["AI_PROVIDER"].strip().lower(), "providers": result}


@app.post("/v1/provider-health")
async def provider_health(request: ProviderHealthRequest) -> dict[str, Any]:
    provider = request.provider.strip().lower()
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported AI provider: {provider}")
    return await check_provider_health(provider=provider, model=request.model, api_key=request.api_key, base_url=request.base_url, timeout=min(30.0, max(5.0, REQUEST_TIMEOUT)))


@app.get("/v1/capabilities")
async def capabilities() -> dict[str, Any]:
    active = CONFIG["AI_PROVIDER"].strip().lower()
    return {"provider": active, "model": CONFIG.get("OLLAMA_MODEL") if active == "ollama" else None, "providers": SUPPORTED_PROVIDERS, "capabilities": ["structured_output", "provider_routing", "document_intelligence", "search_reasoning", "opportunity_reasoning", "research_synthesis", "multi_provider", "fallback_routing", "usage_policy_ready", "provider_health", "native_streaming", "native_thinking_telemetry"]}


@app.post("/v1/configure")
async def configure(request: ConfigureRequest) -> dict[str, Any]:
    provider = request.provider.strip().lower()
    if provider not in SUPPORTED_PROVIDERS: raise HTTPException(status_code=400, detail=f"Unsupported AI provider: {provider}")
    if provider != "ollama" and not request.api_key: raise HTTPException(status_code=400, detail=f"API key is required for {provider} when configuring the gateway directly")
    CONFIG["AI_PROVIDER"] = provider
    if request.model: CONFIG[f"{provider.upper()}_MODEL"] = request.model
    if request.base_url: CONFIG[f"{provider.upper()}_BASE_URL"] = request.base_url.rstrip("/")
    if request.api_key: CONFIG[f"{provider.upper()}_API_KEY"] = request.api_key
    return {"active_provider": provider, "provider": await _configured_provider(provider).health()}


@app.post("/v1/generate")
async def generate(request: GenerateRequest) -> dict[str, Any]:
    provider_name = (request.provider or CONFIG["AI_PROVIDER"]).strip().lower()
    try:
        provider = build_provider(_provider_config(request, provider_name), REQUEST_TIMEOUT)
        result = await provider.generate(prompt=request.prompt, system=request.system, response_schema=request.response_schema, temperature=request.temperature)
        if not result.response or not result.response.strip(): raise ProviderError(f"{provider_name} returned an empty response")
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"provider": result.provider, "model": result.model, "response": result.response, "done": result.done, "total_duration": result.total_duration, "input_tokens": result.input_tokens, "output_tokens": result.output_tokens}


@app.post("/v1/generate/stream")
async def generate_stream(request: GenerateRequest):
    """Normalize provider-native generation into newline-delimited JSON events."""
    provider_name = (request.provider or CONFIG["AI_PROVIDER"]).strip().lower()

    async def events():
        try:
            provider = build_provider(_provider_config(request, provider_name), REQUEST_TIMEOUT)
            yield json.dumps({"type": "started", "provider": provider_name, "model": getattr(provider, "model", request.model)}, ensure_ascii=False) + "\n"
            if isinstance(provider, OllamaProvider):
                payload: dict[str, Any] = {"model": provider.model, "prompt": request.prompt, "stream": True, "options": {"temperature": request.temperature}}
                if request.system: payload["system"] = request.system
                if request.response_schema: payload["format"] = request.response_schema
                if request.think is not None: payload["think"] = request.think
                async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                    async with client.stream("POST", f"{provider.base_url}/api/generate", json=payload) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if not line.strip(): continue
                            yield json.dumps(normalize_ollama_chunk(json.loads(line), provider.name, provider.model), ensure_ascii=False) + "\n"
                return
            result = await provider.generate(prompt=request.prompt, system=request.system, response_schema=request.response_schema, temperature=request.temperature)
            if not result.response or not result.response.strip(): raise ProviderError(f"{provider_name} returned an empty response")
            yield json.dumps({"type": "chunk", "provider": result.provider, "model": result.model, "response": result.response, "done": True, "total_duration": result.total_duration, "input_tokens": result.input_tokens, "output_tokens": result.output_tokens}, ensure_ascii=False) + "\n"
        except (ProviderError, httpx.HTTPError, json.JSONDecodeError) as exc:
            yield json.dumps({"type": "error", "provider": provider_name, "error": str(exc)[:1600]}, ensure_ascii=False) + "\n"

    return StreamingResponse(events(), media_type="application/x-ndjson")
