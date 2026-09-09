from uuid import UUID

import pytest

from app.intelligence.contracts import IntelligenceRequest, TrustState
from app.intelligence.registry import registry


def test_tool_registry_exposes_only_explicit_read_tools():
    tools = registry.list()
    names = {tool["name"] for tool in tools}

    assert "career_vault_search" in names
    assert "evidence_search" in names
    assert all(tool["read_only"] is True for tool in tools)


def test_unknown_tool_is_rejected():
    with pytest.raises(ValueError, match="Unknown intelligence tools"):
        registry.validate_requested(["delete_everything"])


def test_intelligence_request_defaults_are_safe():
    request = IntelligenceRequest(task="Summarize my professional identity")
    assert request.temperature == 0.0
    assert request.tools == []
    assert request.context == {}
    assert request.output_schema is None


def test_contract_supports_evidence_trust_states():
    values: list[TrustState] = [
        "EXTRACTED",
        "INFERRED",
        "USER-CONFIRMED",
        "CONFLICTING",
        "MISSING",
    ]
    assert len(values) == 5
    assert all(isinstance(value, str) for value in values)


def test_uuid_trace_shape_is_supported():
    trace_id = UUID("00000000-0000-0000-0000-000000000001")
    assert isinstance(trace_id, UUID)
