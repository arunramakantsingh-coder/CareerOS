from app.intelligence.identity_reconciliation import _normalize_date, _parse_model_result, _sanitize_experience


def test_ai_reconciliation_normalizes_common_dates():
    assert _normalize_date("Aug 2025") == "2025-08-01"
    assert _normalize_date("2025-07") == "2025-07-01"
    assert _normalize_date("2024") == "2024-01-01"
    assert _normalize_date("not-a-date") is None


def test_ai_reconciliation_sanitizes_structured_experience():
    value = _sanitize_experience({
        "organization": " Cognizant ",
        "client": " Allianz Group ",
        "title": " SR. CYBER SECURITY ARCHITECT ",
        "start_date": "Aug 2025",
        "end_date": None,
        "is_current": True,
        "responsibilities": ["Governance", "Governance"],
        "achievements": ["Reduced risk"],
        "technologies": ["Sentinel", "AlgoSec"],
        "industries": ["Banking"],
        "confidence": 0.93,
        "evidence_excerpt": "SR. CYBER SECURITY ARCHITECT | COGNIZANT (CLIENT: ALLIANZ GROUP)",
    })
    assert value["organization"] == "Cognizant"
    assert value["client"] == "Allianz Group"
    assert value["title"] == "SR. CYBER SECURITY ARCHITECT"
    assert value["start_date"] == "2025-08-01"
    assert value["responsibilities"] == ["Governance"]
    assert value["confidence"] == 0.93


def test_ai_reconciliation_accepts_json_payload_only():
    payload = _parse_model_result('{"experiences": [{"organization": "Cognizant", "title": "Architect"}]}')
    assert payload["experiences"][0]["organization"] == "Cognizant"
