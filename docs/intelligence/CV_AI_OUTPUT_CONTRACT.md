# CareerOS Generic CV AI Output Contract

## Purpose

CareerOS uses AI to understand a CV and return normalized career facts. The AI is **not** responsible for database mapping, ATS rendering, reconciliation policy, personas, recommendations, or UI behavior.

The contract is intentionally small and industry-neutral so the same contract can be used with local Ollama models and cloud AI providers.

## AI instruction

> Read the CV and return the information in the supplied JSON format.
> Use only facts present in the CV. Do not invent, infer, classify, score, recommend, or rewrite facts.
> Understand the CV's own structure even when headings and layout differ. Keep separate jobs separate.
> Put each fact in the most appropriate JSON section. Use null or [] when information is absent.
> Return JSON only.

## JSON shape

```json
{
  "profile": {
    "full_name": null,
    "title": null,
    "summary": null,
    "location": null,
    "email": null,
    "phone": null,
    "linkedin": null
  },
  "employment": [
    {
      "employer": null,
      "title": null,
      "client": null,
      "start_date": null,
      "end_date": null,
      "location": null,
      "description": null,
      "responsibilities": [],
      "achievements": [],
      "technologies": []
    }
  ],
  "education": [
    {
      "institution": null,
      "degree": null,
      "field_of_study": null,
      "start_date": null,
      "end_date": null,
      "grade": null
    }
  ],
  "certifications": [
    {
      "name": null,
      "issuer": null,
      "issue_date": null,
      "expiry_date": null,
      "credential_reference": null
    }
  ],
  "skills": [],
  "projects": [
    {
      "name": null,
      "description": null,
      "role": null,
      "technologies": []
    }
  ],
  "accomplishments": [
    {
      "title": null,
      "description": null,
      "date": null
    }
  ]
}
```

## Boundary

**AI does:**
- understand different CV layouts and section names;
- extract facts from the supplied document;
- preserve separate employment roles;
- return the agreed JSON.

**CareerOS does:**
- validate the returned JSON;
- normalize dates and values;
- deduplicate facts;
- preserve document provenance and evidence;
- reconcile facts into Career Vault / Professional Profile;
- calculate application-specific fields;
- render ATS/profile UI.

No user-specific profession, employer, industry, database model, persona, or recommendation logic belongs in the AI prompt.
