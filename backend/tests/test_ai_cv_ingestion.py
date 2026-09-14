from app.intelligence.cv_ai_contract import CV_AI_OUTPUT_SCHEMA


def test_ai_cv_contract_is_small_and_industry_neutral():
    properties = CV_AI_OUTPUT_SCHEMA["properties"]
    assert set(properties) == {"profile", "employment", "education", "certifications", "skills", "projects", "accomplishments"}
    assert "personas" not in properties
    assert "industries" not in properties["profile"]["properties"]
    assert "years_experience" not in properties["profile"]["properties"]


def test_ai_cv_contract_uses_simple_skill_names():
    assert CV_AI_OUTPUT_SCHEMA["properties"]["skills"]["items"] == {"type": "string"}


def test_ai_cv_contract_preserves_separate_employment_roles():
    employment = CV_AI_OUTPUT_SCHEMA["properties"]["employment"]
    fields = employment["items"]["properties"]
    assert "employer" in fields
    assert "client" in fields
    assert "title" in fields
    assert "start_date" in fields
    assert "end_date" in fields


def test_ai_cv_contract_has_no_application_specific_database_fields():
    text = str(CV_AI_OUTPUT_SCHEMA)
    assert "CandidateProfile" not in text
    assert "ProfessionalExperience" not in text
    assert "CareerFactEvidence" not in text
