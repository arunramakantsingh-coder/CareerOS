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

    async def generate(
        self,
        *,
        prompt: str,
        system: str | None,
        response_schema: dict[str, Any] | None,
        temperature: float,
    ) -> ProviderResult: ...

    async def health(self) -> dict[str, Any]: ...


class OllamaProvider:
    name = "ollama"

    def __init__(self, base_url: str, model: str, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def generate(
        self,
        *,
        prompt: str,
        system: str | None,
        response_schema: dict[str, Any] | None,
        temperature: float,
    ) -> ProviderResult:
        if not self.model:
            raise ProviderError("Ollama model is not configured")

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
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

        return ProviderResult(
            provider=self.name,
            model=self.model,
            response=body.get("response", ""),
            done=body.get("done", False),
            total_duration=body.get("total_duration"),
        )

    async def health(self) -> dict[str, Any]:
        if not self.model:
            return {
                "provider": self.name,
                "configured": False,
                "model": None,
                "reachable": False,
            }
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                return {
                    "provider": self.name,
                    "configured": True,
                    "model": self.model,
                    "reachable": True,
                }
        except httpx.HTTPError as exc:
            return {
                "provider": self.name,
                "configured": True,
                "model": self.model,
                "reachable": False,
                "error": str(exc)[:240],
            }


class OpenRouterProvider:
    name = "openrouter"

    def __init__(self, api_key: str, model: str, base_url: str, timeout: float) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def generate(
        self,
        *,
        prompt: str,
        system: str | None,
        response_schema: dict[str, Any] | None,
        temperature: float,
    ) -> ProviderResult:
        if not self.api_key:
            raise ProviderError("OpenRouter API key is not configured")
        if not self.model:
            raise ProviderError("OpenRouter model is not configured")

        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if response_schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "careeros_result",
                    "strict": True,
                    "schema": response_schema,
                },
            }
            payload["provider"] = {"require_parameters": True}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "CareerOS",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            raise ProviderError(f"OpenRouter request failed: {exc}") from exc

        try:
            content = body["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("OpenRouter returned an unexpected response") from exc

        return ProviderResult(
            provider=self.name,
            model=body.get("model", self.model),
            response=content,
            done=True,
        )

    async def health(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "configured": bool(self.api_key and self.model),
            "model": self.model or None,
            "reachable": None,
            "note": "Provider reachability is checked on generation to avoid spending API quota on health probes.",
        }


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str, model: str, timeout: float) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    async def generate(
        self,
        *,
        prompt: str,
        system: str | None,
        response_schema: dict[str, Any] | None,
        temperature: float,
    ) -> ProviderResult:
        if not self.api_key:
            raise ProviderError("Gemini API key is not configured")
        if not self.model:
            raise ProviderError("Gemini model is not configured")

        combined_prompt = f"{system}\n\n{prompt}" if system else prompt
        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": combined_prompt}]}],
            "generationConfig": {"temperature": temperature},
        }
        if response_schema:
            payload["generationConfig"].update(
                {
                    "response_mime_type": "application/json",
                    "response_schema": response_schema,
                }
            )

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
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

        return ProviderResult(provider=self.name, model=self.model, response=text, done=True)

    async def health(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "configured": bool(self.api_key and self.model),
            "model": self.model or None,
            "reachable": None,
            "note": "Provider reachability is checked on generation to avoid spending API quota on health probes.",
        }


def build_provider(config: dict[str, str], timeout: float) -> AIProvider:
    provider_name = config.get("AI_PROVIDER", "ollama").strip().lower()

    if provider_name == "ollama":
        return OllamaProvider(
            base_url=config.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
            model=config.get("OLLAMA_MODEL", ""),
            timeout=timeout,
        )
    if provider_name == "openrouter":
        return OpenRouterProvider(
            api_key=config.get("OPENROUTER_API_KEY", ""),
            model=config.get("OPENROUTER_MODEL", "openrouter/free"),
            base_url=config.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            timeout=timeout,
        )
    if provider_name == "gemini":
        return GeminiProvider(
            api_key=config.get("GEMINI_API_KEY", ""),
            model=config.get("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            timeout=timeout,
        )

    raise ProviderError(f"Unsupported AI provider: {provider_name}")
