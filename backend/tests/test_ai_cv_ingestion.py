from app.intelligence.ai_cv_ingestion import (
    SCHEMA,
    _normalize_experience,
    _parse,
    _parse_date,
)


def test_ai_cv_schema_is_for_profile_building_only():
    properties = SCHEMA["properties"]
    assert set(("profile", "experiences", "skills", "certifications", "education")).issubset(properties)
    assert "personas" not in properties
    assert SCHEMA["required"] == ["profile", "experiences", "skills", "certifications", "education"]


def test_ai_cv_schema_allows_multiple_employers_and_roles():
    experiences = SCHEMA["properties"]["experiences"]
    assert experiences["type"] == "array"
    assert experiences["maxItems"] >= 10
    item = experiences["items"]["properties"]
    assert {"organization", "client", "title", "start_date", "end_date", "is_current"}.issubset(item)
    assert {"responsibilities", "achievements", "technologies", "industries", "confidence"}.issubset(item)


def test_profile_experience_normalization_preserves_multiple_role_fields():
    normalized = _normalize_experience(
        {
            "organization": "CBI Bank",
            "client": "Internal",
            "title": "Senior Network & Security Architect – Consultant",
            "start_date": "2016-07",
            "end_date": "2018-07",
            "is_current": False,
            "responsibilities": ["Architecture", "Architecture"],
            "achievements": ["Improved resilience"],
            "technologies": ["Cisco", "Palo Alto"],
            "industries": ["Banking"],
            "confidence": 0.93,
        },
        "document-id",
    )
    assert normalized["organization"] == "CBI Bank"
    assert normalized["client"] == "Internal"
    assert normalized["title"] == "Senior Network & Security Architect – Consultant"
    assert normalized["start_date"] == "2016-07"
    assert normalized["end_date"] == "2018-07"
    assert normalized["responsibilities"] == ["Architecture"]
    assert normalized["technologies"] == ["Cisco", "Palo Alto"]
    assert normalized["confidence"] == 0.93


def test_profile_date_parser_accepts_common_cv_date_formats():
    assert _parse_date("2025-08").strftime("%Y-%m") == "2025-08"
    assert _parse_date("Aug 2025").strftime("%Y-%m") == "2025-08"
    assert _parse_date("2025").strftime("%Y-%m") == "2025-01"
    assert _parse_date("not-a-date") is None


def test_ai_payload_parser_accepts_json_code_fence():
    payload = _parse('```json\n{"profile": {}, "experiences": [], "skills": [], "certifications": [], "education": []}\n```')
    assert payload["experiences"] == []
