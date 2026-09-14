from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.intelligence.engine_runtime import RoutedIntelligenceEngine
from app.intelligence.provider_validation import ProviderConfigurationError, validate_provider_configuration


def row(name: str, *, active: bool = True, configured: bool = True, capabilities=None, checked_minutes_ago: int = 1, priority: int = 100, reliability=(9, 10), p95=100.0, avg=50.0, operator_primary=False, model="model"):
    successful, checks = reliability
    checked = (datetime.now(timezone.utc) - timedelta(minutes=checked_minutes_ago)).isoformat()
    return SimpleNamespace(provider=name, label=name.title(), model=model, base_url="https://example.invalid", active=active, configured=configured, encrypted_api_key="encrypted" if name != "ollama" else None, priority=priority, capabilities=capabilities or ["structured_output", "reasoning"], routing_policy={"fallback_enabled": True, "daily_request_limit": None, "operator_primary": operator_primary}, metadata_json={"health": {"status": "healthy", "checked_at": checked, "successful_checks": successful, "checks": checks, "consecutive_failures": 0, "p95_latency_ms": p95, "avg_latency_ms": avg, "quota": {}}})


def test_deactivated_provider_never_selected(monkeypatch):
    engine = RoutedIntelligenceEngine(); rows = [row("openrouter", active=False), row("ollama")]
    class FakeDB:
        def query(self, _): return SimpleNamespace(all=lambda: rows)
        def close(self): pass
    monkeypatch.setattr("app.intelligence.engine_runtime.SessionLocal", lambda: FakeDB())
    ranked, excluded = engine._candidate_snapshot("profile_reconciliation", "trace")
    assert [x.provider for x in ranked] == ["ollama"]
    assert any(x["provider"] == "openrouter" and x["reason"] == "deactivated" for x in excluded)


def test_stale_provider_never_selected(monkeypatch):
    engine = RoutedIntelligenceEngine(); rows = [row("openrouter", checked_minutes_ago=60), row("ollama")]
    class FakeDB:
        def query(self, _): return SimpleNamespace(all=lambda: rows)
        def close(self): pass
    monkeypatch.setattr("app.intelligence.engine_runtime.SessionLocal", lambda: FakeDB())
    ranked, excluded = engine._candidate_snapshot("profile_reconciliation", "trace")
    assert [x.provider for x in ranked] == ["ollama"]
    assert any(x["provider"] == "openrouter" and x["reason"] == "health_stale" for x in excluded)


def test_unhealthy_provider_never_selected(monkeypatch):
    engine = RoutedIntelligenceEngine(); bad = row("openrouter"); bad.metadata_json["health"]["status"] = "unhealthy"; rows = [bad, row("ollama")]
    class FakeDB:
        def query(self, _): return SimpleNamespace(all=lambda: rows)
        def close(self): pass
    monkeypatch.setattr("app.intelligence.engine_runtime.SessionLocal", lambda: FakeDB())
    ranked, excluded = engine._candidate_snapshot("profile_reconciliation", "trace")
    assert [x.provider for x in ranked] == ["ollama"]
    assert any(x["provider"] == "openrouter" and x["reason"] == "health_unhealthy_or_not_checked" for x in excluded)


def test_incompatible_provider_excluded_without_stopping_routing(monkeypatch):
    engine = RoutedIntelligenceEngine(); rows = [row("openrouter", capabilities=["structured_output"]), row("ollama")]
    class FakeDB:
        def query(self, _): return SimpleNamespace(all=lambda: rows)
        def close(self): pass
    monkeypatch.setattr("app.intelligence.engine_runtime.SessionLocal", lambda: FakeDB())
    ranked, excluded = engine._candidate_snapshot("profile_reconciliation", "trace")
    assert [x.provider for x in ranked] == ["ollama"]
    assert any(x["provider"] == "openrouter" and "missing_capabilities" in x["reason"] for x in excluded)


def test_multiple_active_providers_are_dynamically_ranked(monkeypatch):
    engine = RoutedIntelligenceEngine(); rows = [row("openrouter", reliability=(8, 10), p95=500, avg=300), row("ollama", reliability=(10, 10), p95=20, avg=10)]
    class FakeDB:
        def query(self, _): return SimpleNamespace(all=lambda: rows)
        def close(self): pass
    monkeypatch.setattr("app.intelligence.engine_runtime.SessionLocal", lambda: FakeDB())
    ranked, _ = engine._candidate_snapshot("profile_reconciliation", "trace")
    assert [x.provider for x in ranked] == ["ollama", "openrouter"]


def test_manual_priority_cannot_override_health(monkeypatch):
    engine = RoutedIntelligenceEngine(); rows = [row("openrouter", checked_minutes_ago=60, priority=1), row("ollama", priority=1000)]
    class FakeDB:
        def query(self, _): return SimpleNamespace(all=lambda: rows)
        def close(self): pass
    monkeypatch.setattr("app.intelligence.engine_runtime.SessionLocal", lambda: FakeDB())
    ranked, _ = engine._candidate_snapshot("profile_reconciliation", "trace")
    assert [x.provider for x in ranked] == ["ollama"]


def test_provider_configuration_isolation():
    with pytest.raises(ProviderConfigurationError): validate_provider_configuration("openrouter", "gemma3:4b", "http://host.docker.internal:11434")
    with pytest.raises(ProviderConfigurationError): validate_provider_configuration("gemini", "gemma3:4b", "")
    config = validate_provider_configuration("openrouter", "openrouter/free", "https://openrouter.ai/api/v1")
    assert config["model"] == "openrouter/free"; assert config["base_url"] == "https://openrouter.ai/api/v1"


def test_failed_primary_falls_back_to_next_eligible(monkeypatch):
    async def exercise():
        engine = RoutedIntelligenceEngine(); primary = row("openrouter", operator_primary=True); fallback = row("ollama")
        monkeypatch.setattr(engine, "_candidate_snapshot", lambda task, trace: ([primary, fallback], [])); monkeypatch.setattr(engine, "_gateway_config", lambda item: {"provider": item.provider, "model": item.model, "base_url": item.base_url, "api_key": "key"}); monkeypatch.setattr(engine, "_record_telemetry", lambda *args, **kwargs: None)
        class Response:
            def __init__(self, ok: bool, provider: str): self.ok, self.provider = ok, provider
            def raise_for_status(self):
                if not self.ok: raise __import__("httpx").HTTPStatusError("bad gateway", request=None, response=SimpleNamespace(status_code=502, text="bad gateway", json=lambda: {"detail": "bad gateway"}))
            def json(self): return {"provider": self.provider, "model": "model", "response": "ok"}
        class Client:
            def __init__(self, *args, **kwargs): self.calls = 0
            async def __aenter__(self): return self
            async def __aexit__(self, *args): return False
            async def post(self, *_args, **_kwargs): self.calls += 1; return Response(self.calls > 1, "ollama" if self.calls > 1 else "openrouter")
        monkeypatch.setattr("app.intelligence.engine_runtime.httpx.AsyncClient", Client)
        result = await engine.generate_direct({"task_type": "profile_reconciliation", "prompt": "test"})
        assert result["provider"] == "ollama"; assert result["routing"]["fallback_used"] is True; assert result["routing"]["attempts"][0]["status"] == "failed"; assert result["routing"]["attempts"][1]["status"] == "success"
    asyncio.run(exercise())
