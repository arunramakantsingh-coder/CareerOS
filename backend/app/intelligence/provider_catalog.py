from __future__ import annotations

import os
from typing import Any


PROVIDER_CATALOG: dict[str, dict[str, Any]] = {
    "ollama": {"label": "Ollama", "category": "local", "model": os.getenv("OLLAMA_MODEL", "gemma3:4b"), "base_url": os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"), "capabilities": ["local", "private", "structured_output", "reasoning"]},
    "openrouter": {"label": "OpenRouter", "category": "cloud", "model": os.getenv("OPENROUTER_MODEL", ""), "base_url": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"), "capabilities": ["routing", "model_choice", "structured_output", "reasoning"]},
    "openai": {"label": "OpenAI", "category": "cloud", "model": "gpt-5.6-luna", "base_url": "https://api.openai.com/v1", "capabilities": ["reasoning", "structured_output", "vision"]},
    "gemini": {"label": "Google Gemini", "category": "cloud", "model": "gemini-3.5-flash-lite", "base_url": "", "capabilities": ["reasoning", "structured_output", "long_context"]},
    "anthropic": {"label": "Anthropic Claude", "category": "cloud", "model": "claude-sonnet-5", "base_url": "https://api.anthropic.com", "capabilities": ["reasoning", "long_context", "structured_output"]},
    "mistral": {"label": "Mistral AI", "category": "cloud", "model": "mistral-large-latest", "base_url": "https://api.mistral.ai/v1", "capabilities": ["reasoning", "structured_output", "document_intelligence"]},
    "xai": {"label": "xAI", "category": "cloud", "model": "grok-4.6", "base_url": "https://api.x.ai/v1", "capabilities": ["reasoning", "vision", "web_search"]},
    "groq": {"label": "Groq", "category": "cloud", "model": "llama-4-scout-17b-16e-instruct", "base_url": "https://api.groq.com/openai/v1", "capabilities": ["fast", "structured_output"]},
    "deepseek": {"label": "DeepSeek", "category": "cloud", "model": "deepseek-v4-pro", "base_url": "https://api.deepseek.com", "capabilities": ["reasoning", "coding", "structured_output", "long_context"]},
}


def catalog_item(provider: str) -> dict[str, Any]:
    return PROVIDER_CATALOG[provider]


def catalog_names() -> list[str]:
    return list(PROVIDER_CATALOG)
