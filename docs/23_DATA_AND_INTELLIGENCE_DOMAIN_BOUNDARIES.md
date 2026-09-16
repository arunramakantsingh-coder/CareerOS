# CareerOS — Data & Intelligence Domain Boundaries

## Purpose

CareerOS has two fundamentally different kinds of state and they must not be treated as one dataset:

1. **User-owned career data** — facts and source documents belonging to the user.
2. **Application/intelligence data** — runtime state, AI outputs, provider telemetry, generated job intelligence, matching results and other derived artifacts created by CareerOS.

The AI engine is an application service. It must never become the owner of the user's canonical career data.

## Canonical ownership

```text
USER / TENANT
    │
    ├── Career Domain (user-owned, canonical)
    │   ├── Professional Profile / Career Passport
    │   ├── Career Vault facts
    │   ├── Employment
    │   ├── Education
    │   ├── Certifications
    │   ├── Skills
    │   ├── Projects
    │   ├── Accomplishments
    │   ├── Personas
    │   ├── Documents / source material
    │   └── Evidence / provenance
    │
    └── Intelligence Domain (application-owned, derived)
        ├── AI jobs / runs
        ├── AI input snapshots / hashes
        ├── model/provider/trace metadata
        ├── raw AI candidate outputs
        ├── validation reports
        ├── provider health / quota / telemetry
        └── prompt/schema/version metadata

OPPORTUNITY DOMAIN (future)
    ├── Job sources
    ├── Raw job listings
    ├── Canonical jobs / Job DNA
    ├── Search indexes
    ├── Match results
    └── Skill-gap observations
```

## Database strategy

Do **not** split into multiple physical PostgreSQL databases yet. That would introduce unnecessary distributed-transaction and migration complexity while the product is still being reconciled.

Use this progression instead:

### Phase 1 — current PostgreSQL instance

Use the existing `Tenant` and `User.tenant_id` relationship as the security boundary. Enforce tenant ownership in every user-owned query.

Keep domain ownership explicit in code even while tables remain in the existing database.

### Phase 2 — logical PostgreSQL schemas

Move the domains into logical schemas without changing the product contract:

```text
careeros_core
    tenants
    users
    audit / authentication metadata

careeros_career
    candidate_profiles
    professional_experiences
    candidate_skills
    candidate_education
    candidate_certifications
    documents
    career_fact_evidence
    personas

careeros_intelligence
    intelligence_runs
    intelligence_artifacts
    validation_reports
    provider telemetry

careeros_opportunity
    job_sources
    job_listings
    jobs
    job_dna
    matches
    skill_gaps
```

### Phase 3 — physical separation when scale requires it

The intelligence and opportunity workloads may later move to separate databases or services. The application should already communicate through domain/service contracts so that this becomes an infrastructure decision rather than another product rewrite.

## AI ingestion contract

The correct CV flow is:

```text
Upload source document
        │
        ▼
Document Vault
  raw file + raw extracted text
        │
        ▼
Global Intelligence Engine
        │
        ▼
AI candidate artifact
  provider/model/trace/schema/version
        │
        ▼
Deterministic safety validation
        │
        ▼
Application reconciliation service
        │
        ▼
Canonical Professional Profile / Career Vault
```

Deterministic extraction may assist with file validation, raw text extraction, classification, normalization and safety checks. It must not be the competing owner of CV understanding when the AI-first workflow is active.

## Document Vault rule

Uploading a professional document must not automatically mutate the Professional Profile.

A document upload may:

- store the original file;
- extract raw text;
- calculate hashes;
- classify the document deterministically;
- record ingestion metadata;
- index the source for later use.

AI document understanding and evidence linking must be explicit domain operations. A CV's explicit **Reconcile with AI** action is the operation that promotes CV facts into the Professional Profile.

## AI artifact rule

AI responses are not canonical facts.

Every AI operation should conceptually produce:

```text
IntelligenceRun
    task_type
    tenant_id
    user_id
    source_document_id
    provider
    model
    trace_id
    prompt/schema version
    status
    timing
    usage/cost

IntelligenceArtifact
    run_id
    candidate payload
    validation status
    provenance references
```

The reconciliation service decides which candidate facts become canonical. AI code must not directly own the lifecycle of `CandidateProfile` or its canonical child facts.

## Future Job Intelligence rule

Job-search data is not career-profile data.

A future job ingestion pipeline must be isolated:

```text
Job source → raw listing → normalized job → Job DNA → search index
                                            │
                                            ▼
                                     Matching Engine
                                            │
                                            ▼
                                  derived match / gap data
```

It may read the Career Vault through an explicit read contract, but job records and generated search intelligence must never be stored inside the Professional Profile.

## Provider separation

Provider configuration is platform/application state, not user career data. Provider API keys, health, quotas, routing policy, latency and usage telemetry belong to the Intelligence/Platform domain.

User career data may be sent to a provider only through an explicit intelligence request governed by provider policy and privacy controls.

## Refactoring rule

Do not create another parallel parser or another competing profile builder.

Refactor toward one authoritative path:

```text
Document Vault → Intelligence → Reconciliation → Career Vault
```

Prefer:

```text
EXTEND → REFACTOR → FIX
```

over:

```text
DELETE → REBUILD
```

All future work should preserve this boundary.