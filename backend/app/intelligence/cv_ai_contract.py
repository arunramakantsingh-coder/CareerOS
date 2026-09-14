from __future__ import annotations

from typing import Any

# Deliberately small, industry-neutral contract. The model extracts facts; CareerOS maps them
# into its canonical profile/Career Vault models after validation.
CV_AI_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "profile": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "full_name": {"type": ["string", "null"]},
                "title": {"type": ["string", "null"]},
                "summary": {"type": ["string", "null"]},
                "location": {"type": ["string", "null"]},
                "email": {"type": ["string", "null"]},
                "phone": {"type": ["string", "null"]},
                "linkedin": {"type": ["string", "null"]},
            },
            "required": ["full_name", "title", "summary", "location", "email", "phone", "linkedin"],
        },
        "employment": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "employer": {"type": ["string", "null"]},
                    "title": {"type": ["string", "null"]},
                    "client": {"type": ["string", "null"]},
                    "start_date": {"type": ["string", "null"]},
                    "end_date": {"type": ["string", "null"]},
                    "location": {"type": ["string", "null"]},
                    "description": {"type": ["string", "null"]},
                    "responsibilities": {"type": "array", "items": {"type": "string"}},
                    "achievements": {"type": "array", "items": {"type": "string"}},
                    "technologies": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["employer", "title", "client", "start_date", "end_date", "location", "description", "responsibilities", "achievements", "technologies"],
            },
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "institution": {"type": ["string", "null"]},
                    "degree": {"type": ["string", "null"]},
                    "field_of_study": {"type": ["string", "null"]},
                    "start_date": {"type": ["string", "null"]},
                    "end_date": {"type": ["string", "null"]},
                    "grade": {"type": ["string", "null"]},
                },
                "required": ["institution", "degree", "field_of_study", "start_date", "end_date", "grade"],
            },
        },
        "certifications": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": ["string", "null"]},
                    "issuer": {"type": ["string", "null"]},
                    "issue_date": {"type": ["string", "null"]},
                    "expiry_date": {"type": ["string", "null"]},
                    "credential_reference": {"type": ["string", "null"]},
                },
                "required": ["name", "issuer", "issue_date", "expiry_date", "credential_reference"],
            },
        },
        "skills": {
            "type": "array",
            "items": {"type": "string"},
        },
        "projects": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": ["string", "null"]},
                    "description": {"type": ["string", "null"]},
                    "role": {"type": ["string", "null"]},
                    "technologies": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "description", "role", "technologies"],
            },
        },
        "accomplishments": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": ["string", "null"]},
                    "description": {"type": ["string", "null"]},
                    "date": {"type": ["string", "null"]},
                },
                "required": ["title", "description", "date"],
            },
        },
    },
    "required": ["profile", "employment", "education", "certifications", "skills", "projects", "accomplishments"],
}

CV_AI_INSTRUCTION = """Read the CV and return the information in the supplied JSON format.
Use only facts present in the CV. Do not invent, infer, classify, score, recommend, or rewrite facts.
Understand the CV's own structure even when headings and layout differ. Keep separate jobs separate.
Put each fact in the most appropriate JSON section. Use null or [] when information is absent.
Return JSON only."""
