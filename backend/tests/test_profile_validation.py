from app.intelligence.profile_validation import _duplicate_candidates


def test_duplicate_education_is_detected_across_location_suffix():
    snapshot = {
        "education": [
            {"id": "1", "degree": "Bachelor of Business Administration (BBA)", "institution": "Madurai Kamraj University"},
            {"id": "2", "degree": "Bachelor of Business Administration (BBA)", "institution": "Madurai Kamraj University, Pune, India"},
        ],
        "certifications": [],
        "skills": [],
    }
    findings = _duplicate_candidates(snapshot)
    assert any(item["section"] == "education" for item in findings)


def test_duplicate_certification_is_detected_when_name_is_qualified():
    snapshot = {
        "education": [],
        "certifications": [
            {"id": "1", "name": "CCIE", "issuer": "Cisco"},
            {"id": "2", "name": "Cisco CCIE", "issuer": "Cisco"},
        ],
        "skills": [],
    }
    findings = _duplicate_candidates(snapshot)
    assert any(item["section"] == "certifications" for item in findings)


def test_distinct_certifications_are_not_collapsed():
    snapshot = {
        "education": [],
        "certifications": [
            {"id": "1", "name": "CCIE", "issuer": "Cisco"},
            {"id": "2", "name": "CCNP", "issuer": "Cisco"},
        ],
        "skills": [],
    }
    findings = _duplicate_candidates(snapshot)
    assert findings == []
