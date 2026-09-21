from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

DEFAULT_HEALTH_POLICY: dict[str, Any] = {
    "enabled": True,
    "interval_seconds": 900,
    "grace_seconds": 60,
}
MIN_INTERVAL_SECONDS = 300
MAX_INTERVAL_SECONDS = 21600


def normalize_policy(value: dict[str, Any] | None) -> dict[str, Any]:
    value = value or {}
    interval = int(value.get("interval_seconds", DEFAULT_HEALTH_POLICY["interval_seconds"]))
    interval = max(MIN_INTERVAL_SECONDS, min(MAX_INTERVAL_SECONDS, interval))
    grace = max(0, min(900, int(value.get("grace_seconds", DEFAULT_HEALTH_POLICY["grace_seconds"]))))
    return {"enabled": bool(value.get("enabled", True)), "interval_seconds": interval, "grace_seconds": grace}


def policy_from_rows(rows: Iterable[Any]) -> dict[str, Any]:
    for row in rows:
        metadata = row.metadata_json or {}
        if isinstance(metadata.get("health_policy"), dict):
            return normalize_policy(metadata["health_policy"])
    return dict(DEFAULT_HEALTH_POLICY)


def apply_policy_to_rows(rows: Iterable[Any], policy: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_policy(policy)
    for row in rows:
        metadata = dict(row.metadata_json or {})
        metadata["health_policy"] = normalized
        row.metadata_json = metadata
    return normalized


def health_ttl_seconds(policy: dict[str, Any]) -> int:
    normalized = normalize_policy(policy)
    return normalized["interval_seconds"] + normalized["grace_seconds"]


def health_is_fresh(row: Any, ttl_seconds: int) -> bool:
    health = (row.metadata_json or {}).get("health") or {}
    if health.get("status") != "healthy" or not health.get("checked_at"):
        return False
    try:
        checked = datetime.fromisoformat(str(health["checked_at"]).replace("Z", "+00:00"))
    except ValueError:
        return False
    return (datetime.now(timezone.utc) - checked).total_seconds() <= ttl_seconds
