from __future__ import annotations

from urllib.parse import urlparse

from app.intelligence.provider_catalog import PROVIDER_CATALOG


class ProviderConfigurationError(ValueError):
    """Raised when a provider configuration belongs to another adapter/provider."""


def _host(value: str | None) -> str:
    if not value:
        return ""
    try:
        return (urlparse(value).hostname or "").lower()
    except ValueError:
        return ""


def validate_provider_configuration(provider: str, model: str | None, base_url: str | None) -> dict[str, str | None]:
    name = provider.strip().lower()
    if name not in PROVIDER_CATALOG:
        raise ProviderConfigurationError(f"Unsupported Intelligence provider: {name}")

    meta = PROVIDER_CATALOG[name]
    selected_model = (model or meta["model"] or "").strip()
    selected_url = (base_url if base_url is not None else meta["base_url"] or "").strip().rstrip("/")
    host = _host(selected_url)

    # A local Ollama model/endpoint is never valid for a cloud provider.
    if name != "ollama" and (selected_model.lower() == "gemma3:4b" or host in {"host.docker.internal", "localhost", "127.0.0.1"}):
        raise ProviderConfigurationError(
            f"{meta['label']} cannot use an Ollama/local configuration ({selected_model} / {selected_url or 'local endpoint'})."
        )

    if name == "ollama":
        if not selected_url:
            selected_url = meta["base_url"]
        if host not in {"host.docker.internal", "localhost", "127.0.0.1"}:
            raise ProviderConfigurationError("Ollama requires a local Ollama endpoint.")
        if not selected_model or ":" not in selected_model:
            raise ProviderConfigurationError("Ollama requires an Ollama model tag such as gemma3:4b.")

    if name == "gemini":
        # GeminiProvider owns the Google endpoint; allowing an arbitrary base URL
        # here would mix adapter semantics and can route Gemini through Ollama.
        if base_url and host not in {"generativelanguage.googleapis.com"}:
            raise ProviderConfigurationError("Google Gemini uses the native Google API endpoint; do not configure an Ollama/OpenAI-compatible base URL.")
        if not selected_model.lower().startswith("gemini-"):
            raise ProviderConfigurationError("Google Gemini requires a Gemini model id (for example gemini-3.5-flash-lite), not an Ollama model tag.")
        selected_url = ""

    if name == "openrouter":
        if host and host != "openrouter.ai":
            raise ProviderConfigurationError("OpenRouter requires the OpenRouter API endpoint; an Ollama/local endpoint is not valid.")
        if not selected_model or selected_model.lower() == "gemma3:4b":
            raise ProviderConfigurationError("OpenRouter requires an OpenRouter model id such as openrouter/free or provider/model.")
        selected_url = selected_url or meta["base_url"]

    return {"provider": name, "model": selected_model, "base_url": selected_url or None}
