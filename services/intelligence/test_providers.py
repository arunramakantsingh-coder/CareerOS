from providers import GeminiProvider, OllamaProvider, OpenRouterProvider, ProviderError, build_provider


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


def test_build_openrouter_provider():
    provider = build_provider(
        {
            "AI_PROVIDER": "openrouter",
            "OPENROUTER_API_KEY": "test-key",
            "OPENROUTER_MODEL": "openrouter/free",
        },
        timeout=30,
    )
    assert isinstance(provider, OpenRouterProvider)
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
