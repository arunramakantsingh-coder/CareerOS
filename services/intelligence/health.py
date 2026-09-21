from __future__ import annotations

import time
from typing import Any

import httpx


_DEFAULT_OPENROUTER_MODEL = "google/gemma-4-26b-a4b-it:free"

DEFAULTS = {
    "openrouter": ("https://openrouter.ai/api/v1", _DEFAULT_OPENROUTER_MODEL),
    "openai": ("https://api.openai.com/v1", "gpt-5.6-luna"),
    "mistral": ("https://api.mistral.ai/v1", "mistral-large-latest"),
    "xai": ("https://api.x.ai/v1", "grok-4.6"),
    "groq": ("https://api.groq.com/openai/v1", "llama-4-scout-17b-16-instruct"),
    "deepseek": ("https://api.deepseek.com", "deepseek-v4-pro"),
    "ainterceptor": ("https://ainterceptor.taila2310c.ts.net/v1", "deepseek"),
}


def _quota(headers: httpx.Headers) -> dict[str, Any]:
    mapping = {
        "requests_remaining": ("x-ratelimit-remaining-requests", "x-ratelimit-remaining"),
        "requests_limit": ("x-ratelimit-limit-requests",),
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


def _key_usage(body: Any) -> dict[str, Any]:
    data = body.get("data", body) if isinstance(body, dict) else {}
    if not isinstance(data, dict):
        return {}
    keys = ("usage", "usage_daily", "usage_weekly", "usage_monthly", "limit_remaining", "limit", "limit_reset")
    return {key: data[key] for key in keys if key in data}


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
    result: dict[str, Any] = {"provider": name, "model": selected_model, "status": "unhealthy", "reachable": False, "quota": {}}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if name == "ollama":
                url = (base_url or "http://host.docker.internal:11434").rstrip("/") + "/api/tags"
                response = await client.get(url); response.raise_for_status(); body = response.json()
                models = {str(item.get("name")) for item in body.get("models", []) if isinstance(item, dict)}
                if selected_model and models and selected_model not in models: result["error"] = f"Configured model is not available: {selected_model}"
                else: result["status"] = "healthy"; result["reachable"] = True
            elif name == "gemini":
                if not api_key: raise ValueError("Gemini API key is not configured")
                response = await client.get("https://generativelanguage.googleapis.com/v1beta/models", params={"key": api_key, "pageSize": 1000}); response.raise_for_status(); body = response.json()
                names = {str(item.get("name", "")).rsplit("/", 1)[-1] for item in body.get("models", []) if isinstance(item, dict)}
                if selected_model and names and selected_model not in names: result["error"] = f"Configured model is not available: {selected_model}"
                else: result["status"] = "healthy"; result["reachable"] = True
                result["quota"] = _quota(response.headers)
            elif name == "anthropic":
                if not api_key: raise ValueError("Anthropic API key is not configured")
                url = (base_url or "https://api.anthropic.com").rstrip("/") + "/v1/models"; response = await client.get(url, headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"}); response.raise_for_status(); body = response.json()
                ids = {str(item.get("id")) for item in body.get("data", []) if isinstance(item, dict)}; result["status"] = "healthy" if not selected_model or not ids or selected_model in ids else "unhealthy"; result["reachable"] = True
                if result["status"] != "healthy": result["error"] = f"Configured model is not available: {selected_model}"
                result["quota"] = _quota(response.headers)
            elif name == "openrouter":
                if not api_key: raise ValueError("OpenRouter API key is not configured")
                root = (base_url or DEFAULTS[name][0]).rstrip("/")
                key_response = await client.get(root + "/key", headers={"Authorization": f"Bearer {api_key}"}); key_response.raise_for_status()
                quota = _key_usage(key_response.json()); quota.update(_quota(key_response.headers)); result["quota"] = quota
                response = await client.get(root + "/models", headers={"Authorization": f"Bearer {api_key}"}); response.raise_for_status(); body = response.json()
                ids = {str(item.get("id")) for item in body.get("data", []) if isinstance(item, dict)}; result["status"] = "healthy" if not selected_model or not ids or selected_model in ids else "unhealthy"; result["reachable"] = True
                if result["status"] != "healthy": result["error"] = f"Configured model is not available: {selected_model}"
                for key, value in _quota(response.headers).items(): result["quota"].setdefault(key, value)
            elif name == "ainterceptor":
                if not api_key: raise ValueError("AInterceptor API key is not configured")
                root = (base_url or DEFAULTS[name][0]).rstrip("/")
                payload = {"model": selected_model, "messages": [{"role": "user", "content": "health check"}], "stream": False, "max_tokens": 5}
                response = await client.post(root + "/chat/completions", headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json=payload)
                response.raise_for_status()
                result["status"] = "healthy"
                result["reachable"] = True
                result["quota"] = _quota(response.headers)
            elif name in DEFAULTS:
                if not api_key: raise ValueError(f"{name} API key is not configured")
                default_url, _ = DEFAULTS[name]; url = (base_url or default_url).rstrip("/") + "/models"; response = await client.get(url, headers={"Authorization": f"Bearer {api_key}"}); response.raise_for_status(); body = response.json()
                ids = {str(item.get("id")) for item in body.get("data", []) if isinstance(item, dict)}; result["status"] = "healthy" if not selected_model or not ids or selected_model in ids else "unhealthy"; result["reachable"] = True
                if result["status"] != "healthy": result["error"] = f"Configured model is not available: {selected_model}"
                result["quota"] = _quota(response.headers)
            else:
                raise ValueError(f"Unsupported AI provider: {name}")
    except Exception as exc:
        result["error"] = str(exc)[:500]
    result["latency_ms"] = round((time.perf_counter() - started) * 1000, 1)
    return result
