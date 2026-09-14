from providers import GeminiProvider, OllamaProvider, OpenAICompatibleProvider, ProviderError, build_provider


def test_build_provider_defaults_to_ollama():
    provider = build_provider(
        {
            "AI_PROVIDER": "ollama",
            "OLLAMA_BASE_URL": "http://example:11434",
            "OLLAMA_MODEL": "gemma3:4b",
        },
        timeout=30,
    )
    assert isinstance(provider, OllamaProvider)
    assert provider.model == "gemma3:4b"


def test_build_openrouter_provider_uses_explicit_model():
    provider = build_provider(
        {
            "AI_PROVIDER": "openrouter",
            "OPENROUTER_API_KEY": "test-key",
            "OPENROUTER_MODEL": "google/gemma-4-26b-a4b-it:free",
        },
        timeout=30,
    )
    assert isinstance(provider, OpenAICompatibleProvider)
    assert provider.name == "openrouter"
    assert provider.model == "google/gemma-4-26b-a4b-it:free"
    assert provider.base_url == "https://openrouter.ai/api/v1"


def test_build_openrouter_legacy_router_value_is_not_silently_selected():
    provider = build_provider(
        {
            "AI_PROVIDER": "openrouter",
            "OPENROUTER_API_KEY": "test-key",
            "OPENROUTER_MODEL": "openrouter/free",
        },
        timeout=30,
    )
    # The low-level gateway remains provider-neutral; the backend registry validator
    # is responsible for rejecting the dynamic router before runtime selection.
    assert isinstance(provider, OpenAICompatibleProvider)
    assert provider.name == "openrouter"
    assert provider.model == "openrouter/free"


def test_build_gemini_provider():
    provider = build_provider(
        {
            "AI_PROVIDER": "gemini",
            "GEMINI_API_KEY": "test-key",
            "GEMINI_MODEL": "gemini-3.5-flash-lite",
        },
        timeout=30,
    )
    assert isinstance(provider, GeminiProvider)
    assert provider.model == "gemini-3.5-flash-lite"


def test_unknown_provider_is_rejected():
    try:
        build_provider({"AI_PROVIDER": "unknown"}, timeout=30)
    except ProviderError as exc:
        assert "Unsupported AI provider" in str(exc)
    else:
        raise AssertionError("Unknown provider should raise ProviderError")
