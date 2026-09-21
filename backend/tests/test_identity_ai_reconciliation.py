from app.intelligence.ai_cv_ingestion import _date, _normalize_payload, _parse


def test_ai_cv_normalizes_common_dates():
    assert _date("Aug 2025").year == 2025
    assert _date("Aug 2025").month == 8
    assert _date("2025-07").month == 7
    assert _date("2024").year == 2024
    assert _date("not-a-date") is None


def test_ai_cv_accepts_json_payload_only():
    payload = _parse('{"profile": {"full_name": "Arun Singh"}, "employment": []}')
    assert payload["profile"]["full_name"] == "Arun Singh"


def test_ai_cv_normalizes_missing_sections_to_empty_collections():
    payload = _normalize_payload({"profile": {"full_name": "Arun Singh"}})
    assert payload["employment"] == []
    assert payload["education"] == []
    assert payload["certifications"] == []
    assert payload["skills"] == []
    assert payload["projects"] == []
    assert payload["accomplishments"] == []
