# CareerOS — Architecture Evolution & Global Intelligence Runtime

**Status:** Current authoritative engineering decision for M02 / v0.2
**Updated:** 2026-09-14
**Scope:** CV-to-Professional-Profile ingestion, Global Intelligence Engine, provider routing, fallback, usage/cost controls, health/latency/quota, and AI persistence boundaries.

## 1. Why this document exists

CareerOS evolved from an earlier deterministic extraction foundation toward a reusable Global Intelligence Engine. Older documents describe deterministic parsing as the preferred first step; that remains valid as a foundation for document preprocessing, validation, normalization, and safety, but it is **not the primary CV-understanding mechanism for the current CV Profile workflow**.

This document resolves that evolution so future AI/coding sessions do not revert the current product architecture to a regex-first CV parser.

## 2. Current product decision — CV Profile workflow

The primary Professional Profile creation workflow is:

```text
CV Upload
  ↓
PDF/document text extraction
  ↓
Global Intelligence Engine
  ↓
AI semantic understanding of the complete CV
  ↓
Structured Professional Profile candidate facts
  ↓
CareerOS validation / reconciliation / provenance / trust policy
  ↓
Professional Profile + Career Vault
```

The AI must understand the CV semantically even when PDF text is flattened, reordered, or section headings are imperfect. It must identify real employment roles, including multiple roles at the same employer, and extract employer, optional client, title, dates, current status, responsibilities, achievements, technologies, industries and confidence.

AI extraction is therefore **primary for CV understanding**. Deterministic parsing may support preprocessing, structural validation, source verification, normalization, or a safe fallback, but application logic must not require exact CV headings or regex structure for the primary AI profile workflow.

## 3. Separation of product responsibilities

```text
CV
 ↓
Professional Profile / Career Vault intelligence
 ↓
Completed Professional Profile
 ↓
Persona Engine
 ↓
JD / Opportunity Intelligence
```

Separately:

```text
Other professional documents
 ↓
Professional Document Vault
 ↓
Classification / indexing / provenance
```

Personas are built later from the completed professional profile/Career Vault facts. Persona generation is not part of the CV ingestion task.

## 4. AI is not the system of record

The Intelligence Engine produces candidate facts, classifications and recommendations. It does not directly own application state.

```text
CV
 ↓
Intelligence Engine
 ↓
Structured AI result
 ↓
CareerOS validation
 ↓
Deduplication / reconciliation
 ↓
Provenance + trust state
 ↓
Policy
 ↓
Database
```

CareerOS application services remain authoritative for persistence, validation, provenance, permissions and state transitions.

High-confidence, source-backed CV facts may be automatically applied according to policy. Ambiguous, conflicting, or low-confidence changes require review.

### Critical safety rule

An empty AI section is **not** an instruction to delete existing CareerOS facts.

For example:

```text
AI returns experiences = []
```

must never be interpreted as:

```text
user has no employment history
```

It means the extraction result did not provide employment facts. Existing verified/protected data must be preserved, and the result should be handled according to retry/review policy.

## 5. Global Intelligence Engine

All AI workloads must pass through one provider-neutral runtime boundary:

```text
CareerOS feature
    ↓
Global Intelligence Runtime
    ↓
Deterministic Task Router
    ↓
Provider Gateway / Adapter
    ↓
Approved Provider
```

No application feature should call OpenRouter, OpenAI, Gemini, Anthropic, Ollama, or another AI vendor directly.

The engine is platform-wide and multi-user. Provider configuration/credentials are platform-scoped and securely stored. Career/profile/document data remains tenant/user scoped.

## 6. Task-based routing — runtime capability

Routing is deterministic and policy-driven. Do not use an LLM to decide which provider should perform a task initially.

Routing inputs include:

- task type
- required capability
- configured provider availability
- provider health
- priority
- latency policy
- cost policy
- daily/platform quota
- data classification / provider allowlist

Initial workload policy:

| Task | Required capability / routing intent |
|---|---|
| `cv_extraction` | fast + structured output |
| `profile_reconciliation` | reasoning + structured output |
| `document_classification` | fast + low cost + structured output |
| `persona_generation` | reasoning |
| `jd_analysis` | reasoning + long context where needed |
| `matching` | reasoning + structured output |
| `research` | long context / retrieval |
| `interview_intelligence` | reasoning |
| `embedding` | embedding capability |
| `bulk_processing` | cheapest acceptable + structured output |
| `general` | structured output |

The router should prefer the active provider when compatible, then select other configured providers by deterministic policy. Provider/model names must not be hard-coded inside individual CareerOS features.

## 7. Fallback routing — runtime capability

Fallback is an explicit ordered policy, not silent retry behavior.

Example:

```text
CV extraction
  ↓
OpenRouter
  ↓ timeout / 429 / retryable 5xx
Gemini
  ↓ failure
Ollama / approved local provider
```

Only retryable failures should trigger fallback. Each attempt must record:

- request/trace ID
- provider
- model
- start/end time
- latency
- result status
- error/reason
- whether it was a fallback attempt

The final result must identify the actual provider. The UI must not claim that the primary provider completed the task when a fallback actually produced the result.

Fallback is also constrained by data classification and provider allowlists. Confidential or restricted career data cannot be sent to an otherwise available provider that is not approved for that classification.

## 8. Usage & cost controls — runtime capability

The gateway is the central usage accounting boundary. Every AI request should be attributable to:

- request ID / trace ID
- tenant/user
- feature
- task
- provider
- model
- start/end time
- latency
- input tokens when reported
- output tokens when reported
- total tokens when reported
- estimated cost when reliably calculable
- fallback used
- success/failure
- error code

CareerOS-enforced request limits are separate from provider-reported quota/credits.

**Never fabricate token counts, pricing, or cost.** When a provider does not expose reliable usage/pricing information, show `Not reported`, `Unavailable`, or another explicit non-fabricated state.

Current implementation uses the existing provider configuration metadata for runtime telemetry and enforces a CareerOS daily request limit without requiring a new usage-ledger migration for this milestone. A dedicated durable usage ledger may be introduced later when justified.

## 9. Health / latency / quota — runtime capability

Project Control must expose live operational data rather than decorative numbers.

Provider health should include, where available:

- current health/status
- last successful request
- last failure
- consecutive failures
- request count
- failure count
- fallback count
- last latency
- average latency
- P50/P95/P99 latency when sample volume supports meaningful statistics
- provider quota/rate-limit information where exposed by the provider

The UI must distinguish:

```text
CareerOS-enforced policy/quota
        ≠
Provider-reported quota/credits
        ≠
Provider rate-limit signals
```

When data is unavailable, display an explicit no-data state rather than inventing values.

## 10. Project Control — four live intelligence controls

The Project Control → Intelligence Engine surface is not merely a provider settings page. The four operational areas are:

### Task-based routing
Shows active routing strategy, task requirements, provider order, and routing decisions.

### Fallback routing
Shows whether fallback is enabled, fallback counts, attempt history, and policy/health reasons for fallback.

### Usage & cost controls
Shows CareerOS request usage, daily request limits, token usage when reported, and cost when reliably calculable.

### Health / latency / quota
Shows provider health, latency telemetry, errors, rate-limit/quota information and data availability.

Every displayed value must come from backend runtime state. Use `No data yet`, `Not reported`, or `Unavailable` when appropriate.

## 11. CV Intelligence Job lifecycle

CV reconciliation is asynchronous because AI calls can be slow and provider fallback can take multiple attempts.

Required lifecycle:

```text
queued
 → validating_document
 → extracting_context
 → routing
 → ai_processing
 → validating_result
 → reconciling_profile
 → persisting
 → completed / failed
```

The backend owns job state. The frontend must not simulate progress with timers.

The user may keep the processing panel open or run the operation in the background while a persistent activity indicator remains available.

## 12. Current provider foundation

The current provider-neutral catalog includes:

- Ollama
- OpenRouter
- OpenAI-compatible provider adapter/catalog entries
- Google Gemini
- Anthropic
- Mistral AI
- xAI
- Groq
- DeepSeek

Provider credentials are not persisted in the frontend. Save and Activate are separate lifecycle actions. Provider switching must not silently reuse a previously entered secret when the product policy requires the key to be re-entered.

## 13. Current implementation state for this milestone

The current PR #25 branch contains the first operational version of:

- provider-neutral registry and encrypted credential storage
- deterministic task-based routing
- fallback routing with attempt tracking
- request/failure/fallback/latency telemetry
- CareerOS daily request-limit enforcement
- Project Control observability
- explicit non-fabricated token/cost states
- asynchronous CV reconciliation job UX
- database migration compatibility/safety controls

The current runtime telemetry is stored in existing provider configuration metadata for this milestone. Token/cost reporting remains dependent on what the provider gateway exposes; do not represent unavailable token/cost values as real measurements.

## 14. Evolution rule for future AI agents

When older documentation says:

```text
prefer deterministic parsing first
```

interpret that as the **foundational parsing/validation strategy**, not as permission to replace the current AI-first CV understanding workflow.

For the current M02 CV Profile workflow, the authoritative rule is:

```text
AI semantic CV understanding is primary.
Deterministic parsing is supporting infrastructure.
CareerOS application services own validation and persistence.
```

Do not revert this architecture without an explicit Product Owner decision recorded in the control plane.

## 15. Immediate engineering priority

Continue from the existing Global Intelligence runtime and safe employment-reconciliation work.

The next investigation is the OpenRouter CV extraction result that produced substantial profile data but `experiences = 0`. Determine whether the structured-output schema, prompt, model behavior, response normalization, or reconciliation mapping caused the missing employment section.

Do **not** make the deterministic employment anchor parser the primary fix.

Do not re-upload the existing CV. Do not reset the database. Do not delete Career Vault employment data.

The objective is to make the AI-first CV workflow reliable and safe while retaining deterministic safeguards against destructive persistence behavior.
