from app.intelligence.ai_cv_ingestion import SCHEMA


def test_ai_cv_schema_is_small_profile_extraction_contract():
    properties = SCHEMA["properties"]
    assert set(properties) == {"profile", "experiences", "skills", "certifications", "education"}
    assert "personas" not in properties
    assert "profile" in SCHEMA["required"]
    assert "experiences" in SCHEMA["required"]


def test_ai_cv_profile_fields_are_document_facts_only():
    profile = SCHEMA["properties"]["profile"]
    assert set(profile["properties"]) == {
        "full_name",
        "location",
        "title",
        "summary",
        "primary_email",
        "primary_phone",
        "linkedin_url",
        "industries",
    }


def test_ai_cv_experience_keeps_multiple_roles():
    experiences = SCHEMA["properties"]["experiences"]
    assert experiences["type"] == "array"
    assert experiences["maxItems"] >= 10
    item = experiences["items"]["properties"]
    assert "organization" in item
    assert "client" in item
    assert "title" in item
    assert "start_date" in item
    assert "end_date" in item


def test_ai_cv_skills_are_simple_names():
    skills = SCHEMA["properties"]["skills"]
    assert skills["items"] == {"type": "string"}
