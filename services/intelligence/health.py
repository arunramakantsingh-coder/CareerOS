from __future__ import annotations

import time
from typing import Any

import httpx


DEFAULTS = {
    "openrouter": ("https://openrouter.ai/api/v1", "openrouter/free"),
    "openai": ("https://api.openai.com/v1", "gpt-5.6-luna"),
    "mistral": ("https://api.mistral.ai/v1", "mistral-large-latest"),
    "xai": ("https://api.x.ai/v1", "grok-4.6"),
    "groq": ("https://api.groq.com/openai/v1", "llama-4-scout-17b-16-instruct"),
    "deepseek": ("https://api.deepseek.com", "deepseek-v4-pro"),
}


def _quota(headers: httpx.Headers) -> dict[str, Any]:
    mapping = {
        "requests_remaining": ("x-ratelimit-remaining-requests", "x-ratelimit-remaining"),
        "requests_limit": ("x-ratelimit-limit-requests", "x-ratelimit-limit"),
        "tokens_remaining": ("x-ratelimit-remaining-tokens",),
        "tokens_limit": ("x-ratelimit-limit-tokens",),
        "reset": ("x-ratelimit-reset",),
    }
    out: dict[str, Any] = {}
    for key, names in mapping.items():
        for name in names:
            value = headers.get(name)
            if value is not None:
                out[key] = value
                break
    return out


async def check_provider_health(
    *,
    provider: str,
    model: str | None,
    api_key: str | None,
    base_url: str | None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    name = provider.strip().lower()
    selected_model = model or DEFAULTS.get(name, (None, None))[1]
    started = time.perf_counter()
    result: dict[str, Any] = {
        "provider": name,
        "model": selected_model,
        "status": "unhealthy",
        "reachable": False,
        "quota": {},
    }
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if name == "ollama":
                url = (base_url or "http://host.docker.internal:11434").rstrip("/") + "/api/tags"
                response = await client.get(url)
                response.raise_for_status()
                body = response.json()
                models = {str(item.get("name")) for item in body.get("models", []) if isinstance(item, dict)}
                if selected_model and models and selected_model not in models:
                    result["error"] = f"Configured model is not available: {selected_model}"
                else:
                    result["status"] = "healthy"
                    result["reachable"] = True
            elif name == "gemini":
                if not api_key:
                    raise ValueError("Gemini API key is not configured")
                response = await client.get(
                    "https://generativelanguage.googleapis.com/v1beta/models",
                    params={"key": api_key, "pageSize": 1000},
                )
                response.raise_for_status()
                body = response.json()
                names = {str(item.get("name", "")).rsplit("/", 1)[-1] for item in body.get("models", []) if isinstance(item, dict)}
                if selected_model and names and selected_model not in names:
                    result["error"] = f"Configured model is not available: {selected_model}"
                else:
                    result["status"] = "healthy"
                    result["reachable"] = True
                result["quota"] = _quota(response.headers)
            elif name == "anthropic":
                if not api_key:
                    raise ValueError("Anthropic API key is not configured")
                url = (base_url or "https://api.anthropic.com").rstrip("/") + "/v1/models"
                response = await client.get(url, headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"})
                response.raise_for_status()
                body = response.json()
                ids = {str(item.get("id")) for item in body.get("data", []) if isinstance(item, dict)}
                result["status"] = "healthy" if not selected_model or not ids or selected_model in ids else "unhealthy"
                result["reachable"] = True
                if result["status"] != "healthy":
                    result["error"] = f"Configured model is not available: {selected_model}"
                result["quota"] = _quota(response.headers)
            elif name in DEFAULTS:
                if not api_key:
                    raise ValueError(f"{name} API key is not configured")
                default_url, _ = DEFAULTS[name]
                url = (base_url or default_url).rstrip("/") + "/models"
                response = await client.get(url, headers={"Authorization": f"Bearer {api_key}"})
                response.raise_for_status()
                body = response.json()
                ids = {str(item.get("id")) for item in body.get("data", []) if isinstance(item, dict)}
                result["status"] = "healthy" if not selected_model or not ids or selected_model in ids else "unhealthy"
                result["reachable"] = True
                if result["status"] != "healthy":
                    result["error"] = f"Configured model is not available: {selected_model}"
                result["quota"] = _quota(response.headers)
            else:
                raise ValueError(f"Unsupported AI provider: {name}")
    except Exception as exc:
        result["error"] = str(exc)[:500]
    result["latency_ms"] = round((time.perf_counter() - started) * 1000, 1)
    return result
