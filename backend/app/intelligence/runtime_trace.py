from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any
from uuid import UUID, uuid4

_MAX_TRACES = 100
_MAX_EVENTS = 250
_LOCK = Lock()
_TRACES: deque[dict[str, Any]] = deque(maxlen=_MAX_TRACES)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def start_trace(task_type: str, required_capabilities: list[str], *, context: dict[str, Any] | None = None) -> str:
    trace_id = str(uuid4())
    trace = {
        "trace_id": trace_id,
        "started_at": _now(),
        "updated_at": _now(),
        "status": "running",
        "task_type": task_type,
        "required_capabilities": list(required_capabilities),
        "candidates": [],
        "excluded_candidates": [],
        "selected_provider": None,
        "selected_model": None,
        "ranking_reason": None,
        "attempts": [],
        "fallback_used": False,
        "final_provider": None,
        "total_latency_ms": 0.0,
        "thinking_available": False,
        "thinking_chars": 0,
        "thinking_text": "",
        "output_chars": 0,
        "output_preview": "",
        "provider_metrics": {},
        "events": [],
    }
    if context:
        trace["context"] = {k: str(v)[:500] for k, v in context.items() if k in {"document_id", "filename"}}
    with _LOCK:
        _TRACES.append(trace)
    return trace_id


def _find(trace_id: str) -> dict[str, Any] | None:
    for trace in reversed(_TRACES):
        if trace["trace_id"] == trace_id:
            return trace
    return None


def event(trace_id: str, event_type: str, message: str, **details: Any) -> None:
    with _LOCK:
        trace = _find(trace_id)
        if not trace:
            return
        item = {"timestamp": _now(), "type": event_type, "message": message, **details}
        trace["events"].append(item)
        if len(trace["events"]) > _MAX_EVENTS:
            del trace["events"][:-_MAX_EVENTS]
        trace["updated_at"] = item["timestamp"]


def update(trace_id: str, **values: Any) -> None:
    with _LOCK:
        trace = _find(trace_id)
        if not trace:
            return
        trace.update(values)
        trace["updated_at"] = _now()


def finish(trace_id: str, *, status: str, final_provider: str | None = None, total_latency_ms: float | None = None) -> None:
    update(trace_id, status=status, final_provider=final_provider, total_latency_ms=round(total_latency_ms or 0.0, 1), completed_at=_now())


def get_trace(trace_id: str) -> dict[str, Any] | None:
    with _LOCK:
        trace = _find(trace_id)
        return dict(trace) if trace else None


def list_traces(limit: int = 25) -> list[dict[str, Any]]:
    with _LOCK:
        selected = list(_TRACES)[-max(1, min(limit, _MAX_TRACES)):]
        return [dict(trace) for trace in reversed(selected)]


def as_uuid(trace_id: str | None) -> UUID | None:
    if not trace_id:
        return None
    try:
        return UUID(trace_id)
    except ValueError:
        return None
