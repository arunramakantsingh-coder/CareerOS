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
        if not self.model:
            raise ProviderError("Ollama model is not configured")
        payload: dict[str, Any] = {"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": temperature}}
        if system:
            payload["system"] = system
        if response_schema:
            payload["format"] = response_schema
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            raise ProviderError(f"Ollama request failed: {exc}") from exc
        return ProviderResult(self.name, self.model, body.get("response", ""), body.get("done", False), body.get("total_duration"))

    async def health(self) -> dict[str, Any]:
        if not self.model:
            return {"provider": self.name, "configured": False, "model": None, "reachable": False}
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
            return {"provider": self.name, "configured": True, "model": self.model, "reachable": True}
        except httpx.HTTPError as exc:
            return {"provider": self.name, "configured": True, "model": self.model, "reachable": False, "error": str(exc)[:240]}


class OpenAICompatibleProvider:
    def __init__(self, name: str, api_key: str, model: str, base_url: str, timeout: float) -> None:
        self.name, self.api_key, self.model, self.base_url, self.timeout = name, api_key, model, base_url.rstrip("/"), timeout

    async def generate(self, *, prompt: str, system: str | None, response_schema: dict[str, Any] | None, temperature: float) -> ProviderResult:
        if not self.api_key:
            raise ProviderError(f"{self.name} API key is not configured")
        if not self.model:
            raise ProviderError(f"{self.name} model is not configured")
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": temperature}
        if response_schema:
            payload["response_format"] = {"type": "json_schema", "json_schema": {"name": "careeros_result", "strict": True, "schema": response_schema}}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "X-Title": "CareerOS"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            raise ProviderError(f"{self.name} request failed: {exc}") from exc
        try:
            content = body["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError(f"{self.name} returned an unexpected response") from exc
        return ProviderResult(self.name, body.get("model", self.model), content, True)

    async def health(self) -> dict[str, Any]:
        return {"provider": self.name, "configured": bool(self.api_key and self.model), "model": self.model or None, "reachable": None, "note": "Reachability is checked on generation to avoid quota use."}


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str, model: str, base_url: str, timeout: float) -> None:
        self.api_key, self.model, self.base_url, self.timeout = api_key, model, base_url.rstrip("/"), timeout

    async def generate(self, *, prompt: str, system: str | None, response_schema: dict[str, Any] | None, temperature: float) -> ProviderResult:
        if not self.api_key:
            raise ProviderError("Anthropic API key is not configured")
        messages = [{"role": "user", "content": prompt}]
        payload: dict[str, Any] = {"model": self.model, "max_tokens": 8192, "messages": messages}
        if temperature:
            payload["temperature"] = temperature
        if system:
            payload["system"] = system
        if response_schema:
            payload["output_config"] = {"format": {"type": "json_schema", "schema": response_schema}}
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/v1/messages", json=payload, headers=headers)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            raise ProviderError(f"Anthropic request failed: {exc}") from exc
        try:
            text = body["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("Anthropic returned an unexpected response") from exc
        return ProviderResult(self.name, body.get("model", self.model), text, True)

    async def health(self) -> dict[str, Any]:
        return {"provider": self.name, "configured": bool(self.api_key and self.model), "model": self.model or None, "reachable": None, "note": "Reachability is checked on generation to avoid quota use."}


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str, model: str, timeout: float) -> None:
        self.api_key, self.model, self.timeout = api_key, model, timeout

    async def generate(self, *, prompt: str, system: str | None, response_schema: dict[str, Any] | None, temperature: float) -> ProviderResult:
        if not self.api_key:
            raise ProviderError("Gemini API key is not configured")
        if not self.model:
            raise ProviderError("Gemini model is not configured")
        combined_prompt = f"{system}\n\n{prompt}" if system else prompt
        payload: dict[str, Any] = {"contents": [{"role": "user", "parts": [{"text": combined_prompt}]}], "generationConfig": {"temperature": temperature}}
        if response_schema:
            payload["generationConfig"].update({"response_mime_type": "application/json", "response_schema": response_schema})
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            raise ProviderError(f"Gemini request failed: {exc}") from exc
        try:
            text = body["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("Gemini returned an unexpected response") from exc
        return ProviderResult(self.name, self.model, text, True)

    async def health(self) -> dict[str, Any]:
        return {"provider": self.name, "configured": bool(self.api_key and self.model), "model": self.model or None, "reachable": None, "note": "Reachability is checked on generation to avoid quota use."}


def build_provider(config: dict[str, str], timeout: float) -> AIProvider:
    provider_name = config.get("AI_PROVIDER", config.get("provider", "ollama")).strip().lower()
    api_key = config.get("api_key") or config.get("OPENROUTER_API_KEY") or config.get("GEMINI_API_KEY") or ""
    model = config.get("model") or config.get(f"{provider_name.upper()}_MODEL", "")
    base_url = config.get("base_url") or config.get(f"{provider_name.upper()}_BASE_URL", "")
    if provider_name == "ollama":
        return OllamaProvider(base_url or "http://host.docker.internal:11434", model or config.get("OLLAMA_MODEL", ""), timeout)
    if provider_name == "gemini":
        return GeminiProvider(api_key or config.get("GEMINI_API_KEY", ""), model or "gemini-3.5-flash-lite", timeout)
    if provider_name == "anthropic":
        return AnthropicProvider(api_key, model or "claude-sonnet-5", base_url or "https://api.anthropic.com", timeout)
    defaults = {"openrouter": ("https://openrouter.ai/api/v1", "openrouter/free"), "openai": ("https://api.openai.com/v1", "gpt-5.6-luna"), "mistral": ("https://api.mistral.ai/v1", "mistral-large-latest"), "xai": ("https://api.x.ai/v1", "grok-4.6"), "groq": ("https://api.groq.com/openai/v1", "llama-4-scout-17b-16e-instruct"), "deepseek": ("https://api.deepseek.com/v1", "deepseek-chat")}
    if provider_name in defaults:
        default_url, default_model = defaults[provider_name]
        return OpenAICompatibleProvider(provider_name, api_key, model or default_model, base_url or default_url, timeout)
    raise ProviderError(f"Unsupported AI provider: {provider_name}")
