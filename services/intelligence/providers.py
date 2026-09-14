from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import httpx


class ProviderError(RuntimeError):
    """Raised when an AI provider cannot produce a response."""


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    model: str
    response: str
    done: bool = True
    total_duration: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


class AIProvider(Protocol):
    name: str
    model: str

    async def generate(self, *, prompt: str, system: str | None, response_schema: dict[str, Any] | None, temperature: float) -> ProviderResult: ...
    async def health(self) -> dict[str, Any]: ...


class OllamaProvider:
    name = "ollama"

    def __init__(self, base_url: str, model: str, timeout: float) -> None:
        self.base_url, self.model, self.timeout = base_url.rstrip("/"), model, timeout

    async def generate(self, *, prompt: str, system: str | None, response_schema: dict[str, Any] | None, temperature: float) -> ProviderResult:
        if not self.model: raise ProviderError("Ollama model is not configured")
        payload: dict[str, Any] = {"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": temperature}}
        if system: payload["system"] = system
        if response_schema: payload["format"] = response_schema
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload); response.raise_for_status(); body = response.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:1200] if exc.response is not None else str(exc)
            raise ProviderError(f"Ollama request failed: HTTP {exc.response.status_code if exc.response is not None else 'error'}: {detail}") from exc
        except httpx.HTTPError as exc: raise ProviderError(f"Ollama request failed: {exc}") from exc
        return ProviderResult(self.name, self.model, body.get("response", ""), body.get("done", False), body.get("total_duration"), body.get("prompt_eval_count"), body.get("eval_count"))

    async def health(self) -> dict[str, Any]:
        if not self.model: return {"provider": self.name, "configured": False, "model": None, "reachable": False}
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags"); response.raise_for_status()
            return {"provider": self.name, "configured": True, "model": self.model, "reachable": True}
        except httpx.HTTPStatusError as exc:
            return {"provider": self.name, "configured": True, "model": self.model, "reachable": False, "error": f"HTTP {exc.response.status_code}: {exc.response.text[:240]}"}
        except httpx.HTTPError as exc: return {"provider": self.name, "configured": True, "model": self.model, "reachable": False, "error": str(exc)[:240]}


class OpenAICompatibleProvider:
    def __init__(self, name: str, api_key: str, model: str, base_url: str, timeout: float) -> None:
        self.name, self.api_key, self.model, self.base_url, self.timeout = name, api_key, model, base_url.rstrip("/"), timeout

    async def generate(self, *, prompt: str, system: str | None, response_schema: dict[str, Any] | None, temperature: float) -> ProviderResult:
        if not self.api_key: raise ProviderError(f"{self.name} API key is not configured")
        if not self.model: raise ProviderError(f"{self.name} model is not configured")
        messages: list[dict[str, Any]] = []
        if system: messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": temperature}
        if response_schema:
            if self.name == "openrouter":
                # The selected free Gemma endpoint supports JSON output mode but does
                # not enforce a JSON Schema. CareerOS validates the returned JSON
                # before any profile mutation.
                payload["response_format"] = {"type": "json_object"}
            else:
                payload["response_format"] = {"type": "json_schema", "json_schema": {"name": "careeros_result", "strict": True, "schema": response_schema}}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "X-Title": "CareerOS"}
        if self.name == "openrouter":
            headers["HTTP-Referer"] = "https://careeros.app"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code if exc.response is not None else "error"
            detail = exc.response.text[:1600] if exc.response is not None else str(exc)
            raise ProviderError(f"{self.name} request failed: HTTP {status}: {detail}") from exc
        except httpx.HTTPError as exc: raise ProviderError(f"{self.name} request failed: {exc}") from exc
        try: content = body["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc: raise ProviderError(f"{self.name} returned an unexpected response") from exc
        usage = body.get("usage") or {}
        return ProviderResult(self.name, body.get("model", self.model), content, True, None, usage.get("prompt_tokens"), usage.get("completion_tokens"))

    async def health(self) -> dict[str, Any]:
        return {"provider": self.name, "configured": bool(self.api_key and self.model), "model": self.model or None, "reachable": None, "note": "Reachability is checked by the provider-specific health adapter."}


class AnthropicProvider:
    name = "anthropic"
    def __init__(self, api_key: str, model: str, base_url: str, timeout: float) -> None: self.api_key, self.model, self.base_url, self.timeout = api_key, model, base_url.rstrip("/"), timeout
    async def generate(self, *, prompt: str, system: str | None, response_schema: dict[str, Any] | None, temperature: float) -> ProviderResult:
        if not self.api_key: raise ProviderError("Anthropic API key is not configured")
        payload: dict[str, Any] = {"model": self.model, "max_tokens": 8192, "messages": [{"role": "user", "content": prompt}]}
        if temperature: payload["temperature"] = temperature
        if system: payload["system"] = system
        if response_schema: payload["output_config"] = {"format": {"type": "json_schema", "schema": response_schema}}
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/v1/messages", json=payload); response.raise_for_status(); body = response.json()
        except httpx.HTTPStatusError as exc: raise ProviderError(f"Anthropic request failed: HTTP {exc.response.status_code}: {exc.response.text[:1200]}") from exc
        except httpx.HTTPError as exc: raise ProviderError(f"Anthropic request failed: {exc}") from exc
        try: text = body["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc: raise ProviderError("Anthropic returned an unexpected response") from exc
        usage = body.get("usage") or {}
        return ProviderResult(self.name, body.get("model", self.model), text, True, None, usage.get("input_tokens"), usage.get("output_tokens"))
    async def health(self) -> dict[str, Any]: return {"provider": self.name, "configured": bool(self.api_key and self.model), "model": self.model or None, "reachable": None, "note": "Reachability is checked by the provider-specific health adapter."}


class GeminiProvider:
    name = "gemini"
    def __init__(self, api_key: str, model: str, timeout: float) -> None: self.api_key, self.model, self.timeout = api_key, model, timeout
    async def generate(self, *, prompt: str, system: str | None, response_schema: dict[str, Any] | None, temperature: float) -> ProviderResult:
        if not self.api_key: raise ProviderError("Gemini API key is not configured")
        if not self.model: raise ProviderError("Gemini model is not configured")
        combined_prompt = f"{system}\n\n{prompt}" if system else prompt
        payload: dict[str, Any] = {"contents": [{"role": "user", "parts": [{"text": combined_prompt}]}], "generationConfig": {"temperature": temperature}}
        if response_schema: payload["generationConfig"].update({"response_mime_type": "application/json", "response_schema": response_schema})
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload); response.raise_for_status(); body = response.json()
        except httpx.HTTPStatusError as exc: raise ProviderError(f"Gemini request failed: HTTP {exc.response.status_code}: {exc.response.text[:1200]}") from exc
        except httpx.HTTPError as exc: raise ProviderError(f"Gemini request failed: {exc}") from exc
        try: text = body["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc: raise ProviderError("Gemini returned an unexpected response") from exc
        usage = body.get("usageMetadata") or {}
        return ProviderResult(self.name, self.model, text, True, None, usage.get("promptTokenCount"), usage.get("candidatesTokenCount"))
    async def health(self) -> dict[str, Any]: return {"provider": self.name, "configured": bool(self.api_key and self.model), "model": self.model or None, "reachable": None, "note": "Reachability is checked by the provider-specific health adapter."}


def build_provider(config: dict[str, str], timeout: float) -> AIProvider:
    provider_name = config.get("AI_PROVIDER", config.get("provider", "ollama")).strip().lower()
    model = config.get("model") or config.get(f"{provider_name.upper()}_MODEL", "")
    base_url = config.get("base_url") or config.get(f"{provider_name.upper()}_BASE_URL", "")
    api_key = config.get("api_key") or config.get(f"{provider_name.upper()}_API_KEY", "")
    if provider_name == "ollama": return OllamaProvider(base_url or "http://host.docker.internal:11434", model or config.get("OLLAMA_MODEL", ""), timeout)
    if provider_name == "gemini": return GeminiProvider(api_key, model or "gemini-3.5-flash-lite", timeout)
    if provider_name == "anthropic": return AnthropicProvider(api_key, model or "claude-sonnet-5", base_url or "https://api.anthropic.com", timeout)
    defaults = {"openrouter": ("https://openrouter.ai/api/v1", "google/gemma-4-26b-a4b-it:free"), "openai": ("https://api.openai.com/v1", "gpt-5.6-luna"), "mistral": ("https://api.mistral.ai/v1", "mistral-large-latest"), "xai": ("https://api.x.ai/v1", "grok-4.6"), "groq": ("https://api.groq.com/openai/v1", "llama-4-scout-17b-16e-instruct"), "deepseek": ("https://api.deepseek.com/v1", "deepseek-v4-pro")}
    if provider_name in defaults:
        default_url, default_model = defaults[provider_name]
        return OpenAICompatibleProvider(provider_name, api_key, model or default_model, base_url or default_url, timeout)
    raise ProviderError(f"Unsupported AI provider: {provider_name}")
