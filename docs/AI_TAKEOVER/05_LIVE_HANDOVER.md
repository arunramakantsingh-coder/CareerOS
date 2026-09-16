# CareerOS — LIVE HANDOVER SNAPSHOT

> Update this file at the end of every material AI session. A new AI must be able to continue from GitHub and runtime evidence without relying on prior chat.

## Snapshot

- Date: 2026-09-14
- Active development branch: `feature/intelligence-provider-gateway-20260912`
- Current branch HEAD after documentation updates: `29104e0845a8c0ebe3bc5663e4fbf5e0344c1044`
- Active product release: v0.2 Global Job Intelligence
- Current work: Global Intelligence runtime + safe CV AI reconciliation + architecture/documentation reconciliation
- Current PR: **#25 — feat(intelligence): global intelligence runtime + safe CV employment reconciliation**
- PR state: OPEN / DRAFT
- Release target: `release/v0.2-global-job-intelligence`

## Current architecture decision — authoritative

CareerOS has evolved from the original deterministic extraction foundation toward a reusable Global Intelligence Engine. For the current M02 Professional Profile workflow, **AI semantic CV understanding is primary**.

```text
CV Upload
  ↓
PDF/document text extraction
  ↓
Global Intelligence Engine
  ↓
AI semantic understanding of complete CV
  ↓
Structured candidate facts
  ↓
CareerOS validation / reconciliation / provenance / trust policy
  ↓
Professional Profile / Career Vault
```

Deterministic parsing remains supporting infrastructure for preprocessing, validation, normalization, source verification and safety. It must not become the primary CV-understanding mechanism or make CV ingestion depend on exact headings/regex structure.

Personas are generated later from the completed Professional Profile/Career Vault. They are not generated during CV ingestion.

The authoritative decision record is:

`docs/AI_TAKEOVER/07_ARCHITECTURE_EVOLUTION_AND_GLOBAL_INTELLIGENCE_RUNTIME.md`

## Critical AI persistence safety rule

AI is not the system of record. CareerOS application services own validation, reconciliation, provenance, permissions, state transitions and persistence.

An empty AI section is never permission to delete existing facts.

The recent P0 employment incident was:

```text
OpenRouter CV ingestion succeeded partially
→ skills/certifications/education/projects extracted
→ experiences returned as []
→ old persistence path treated [] as authoritative
→ existing employment records were removed
```

The current safety work prevents an empty AI employment result from becoming a destructive delete path. The employment safety test suite currently reports **5 passed** in the user's local run.

Do not re-upload the existing CV or reset the database while investigating this incident.

## Global Intelligence runtime — current target

The Project Control → Intelligence surface is a real operational control plane, not merely a provider settings page.

### 1. Task-based routing

Deterministic routing based on task/capability, provider health, priority, cost policy, quota and data classification.

Initial tasks:

```text
cv_extraction
profile_reconciliation
document_classification
persona_generation
jd_analysis
matching
research
interview_intelligence
embedding
bulk_processing
general
```

### 2. Fallback routing

Ordered, policy-controlled fallback. Retry only retryable failures. Record every provider attempt, latency, error/reason and actual provider used. Never silently hide a fallback.

Fallback must respect provider/data-classification policy.

### 3. Usage & cost controls

Central gateway attribution for request/trace ID, tenant/user, feature, task, provider, model, latency, status, token usage where reported, and cost only when reliably calculable.

CareerOS request limits are distinct from provider-reported quota/credits. Never fabricate token counts or costs. Use explicit `Not reported`, `Unavailable` or `No data` states.

### 4. Health / latency / quota

Expose actual provider health, failures, fallback counts, latency and provider-reported quota/rate-limit information where available. P50/P95/P99 should only be shown when sufficient samples exist.

## Current runtime implementation

PR #25 contains the first operational implementation of:

- provider-neutral registry and encrypted credentials;
- separate Save Credentials / Activate lifecycle;
- deterministic task-based routing;
- fallback routing with attempt tracking;
- request/failure/fallback/latency telemetry;
- CareerOS daily request-limit enforcement;
- Project Control observability;
- explicit non-fabricated token/cost states;
- asynchronous CV reconciliation job UX;
- database migration compatibility/safety controls.

Runtime telemetry currently reuses existing provider configuration metadata and the existing document processing-status JSON field to avoid a new migration for this milestone. Token/cost reporting remains dependent on provider gateway usage data; do not represent unavailable values as real measurements.

## CV reconciliation job

The current user-facing lifecycle is backend-driven:

```text
queued
→ validating_document
→ routing
→ ai_processing
→ reconciling_profile
→ persisting
→ completed / failed
```

The frontend must poll actual backend state and must not simulate progress with a timer.

## Database safety / migration repair

All material PostgreSQL/Alembic changes remain governed by:

- `docs/AI_TAKEOVER/06_DATABASE_SAFETY.md`
- `docs/DB_MIGRATION_AND_DATABASE_VALIDATION_PROCEDURE.md`
- `docs/DB_SCHEMA_BASELINE.md`
- `backend/scripts/validate_database.py`

Current migration graph:

```text
016_m02_identity_intelligence
        |
017_m02_employment_semantic_fields
        |\
        | \
018_m02_profile_sections   018_intel_provider_registry
        |                     |
        +----------+----------+
                   |
          019_intelligence_registry
```

No database reset, PostgreSQL volume recreation, destructive application-data delete, or CV re-upload is authorized for this work.

Protected untracked files:

```text
backend/backend-openapi.json
cv-extracted.txt
openapi-check.json
```

## Runtime evidence already provided by the user

- Pre-migration database validator passed.
- Backend successfully started after controlled migration repair and reached `019_intelligence_registry`.
- Employment safety tests: `5 passed`.
- Existing CV document ID: `d1307403-ae5b-41ad-b296-d007f910b10b`.
- Existing OpenRouter AI ingestion metadata showed successful AI processing but `experiences: 0`, while also extracting 69 skills, 7 certifications, 2 education and 43 projects.
- Standalone ORM diagnostics encountered an unrelated model-registration error for `ExternalIdentity`; this is not evidence that the CV AI workflow failed.
- Direct deterministic employment-anchor extraction against `cv-extracted.txt` returned `ANCHOR COUNT: 0`. This is only evidence that the supporting anchor parser does not match that extracted text; it is **not** the primary CV intelligence architecture and should not drive the solution.

## Immediate next engineering action

Investigate the AI-first CV ingestion path that produced `experiences = 0`.

Inspect:

1. the structured output schema for employment;
2. the CV extraction prompt and task definition;
3. the OpenRouter request/response normalization;
4. the model response actually persisted in the document metadata;
5. `_apply_experiences()` and surrounding reconciliation mapping;
6. validation behavior for an empty AI section;
7. provider/model behavior and fallback handling.

The goal is:

```text
Existing CV
→ Global Intelligence Engine
→ complete structured profile
→ safe validation/reconciliation
→ Professional Profile / Career Vault
```

Do not make the deterministic employment anchor parser the primary fix.

Do not delete or recreate existing employment records during debugging.

## Documentation reconciliation completed

Added:

`docs/AI_TAKEOVER/07_ARCHITECTURE_EVOLUTION_AND_GLOBAL_INTELLIGENCE_RUNTIME.md`

Updated:

- `docs/00_HANDOFF_INDEX.md`
- `.ai/README.md`
- this live handover

These documents now explicitly record the current AI-first CV decision and the four Global Intelligence runtime controls: task-based routing, fallback routing, usage & cost controls, and health/latency/quota.
