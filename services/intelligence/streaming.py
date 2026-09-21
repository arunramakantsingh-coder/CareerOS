from __future__ import annotations

from typing import Any


OLLAMA_METRIC_FIELDS = (
    "total_duration",
    "load_duration",
    "prompt_eval_count",
    "prompt_eval_duration",
    "eval_count",
    "eval_duration",
    "done_reason",
)


def normalize_ollama_chunk(chunk: dict[str, Any], provider: str, model: str) -> dict[str, Any]:
    """Normalize one native Ollama NDJSON chunk without inventing telemetry."""
    event: dict[str, Any] = {"type": "chunk", "provider": provider, "model": chunk.get("model") or model}
    for key in ("response", "thinking", "done", *OLLAMA_METRIC_FIELDS):
        if key in chunk:
            event[key] = chunk[key]
    return event
