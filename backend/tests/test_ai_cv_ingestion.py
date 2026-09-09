from app.intelligence.ai_cv_ingestion import SCHEMA


def test_ai_cv_schema_is_whole_profile_not_employment_only():
    properties = SCHEMA["properties"]
    assert set(("profile", "experiences", "skills", "certifications", "education", "personas")).issubset(properties)
    assert "profile" in SCHEMA["required"]
    assert "experiences" in SCHEMA["required"]


def test_ai_cv_schema_allows_multiple_employers_and_roles():
    experiences = SCHEMA["properties"]["experiences"]
    assert experiences["type"] == "array"
    assert experiences["maxItems"] >= 10
    item = experiences["items"]["properties"]
    assert "organization" in item
    assert "client" in item
    assert "title" in item
    assert "start_date" in item
    assert "end_date" in item
