# CareerOS — AI CONTROL PLANE

This directory is the persistent, AI-readable control plane for CareerOS.

## Purpose

Any AI agent taking over this repository must be able to reconstruct the project without access to a previous chat session.

Git is the implementation history. The control plane is the continuity layer. Runtime evidence is the truth for whether a feature actually works.

## First read

1. `/AI_TAKEOVER.md`
2. `/AGENTS.md`
3. `/.ai/AI_TAKEOVER_PROTOCOL.md`
4. `/.ai/ROLE_MATRIX.md`
5. `/docs/AI_TAKEOVER/01_PROJECT_REQUIREMENTS_BASELINE.md`
6. `/docs/AI_TAKEOVER/02_CURRENT_STATE_20260903.md`
7. `/docs/AI_TAKEOVER/03_GIT_BRANCH_AND_RELEASE_CONTROL.md`
8. `/docs/AI_TAKEOVER/05_LIVE_HANDOVER.md`
9. `/docs/AI_TAKEOVER/06_DATABASE_SAFETY.md`
10. `/docs/AI_TAKEOVER/07_ARCHITECTURE_EVOLUTION_AND_GLOBAL_INTELLIGENCE_RUNTIME.md`
11. `/docs/DB_MIGRATION_AND_DATABASE_VALIDATION_PROCEDURE.md`
12. `/docs/DB_SCHEMA_BASELINE.md`
13. `/docs/21_AI_TO_AI_COORDINATION_PROTOCOL.md`
14. `/docs/22_CAREEROS_CURRENT_CONTROL_STATE.md`
15. `/docs/23_CAREEROS_MODULE_VERSION_REGISTRY.md`

## Current architecture decision

The current M02 Professional Profile workflow is **AI-first for CV understanding**:

```text
CV Upload
→ PDF/document text extraction
→ Global Intelligence Engine
→ AI semantic CV understanding
→ structured candidate facts
→ CareerOS validation/reconciliation/provenance/trust policy
→ Professional Profile / Career Vault
```

Deterministic parsing remains supporting infrastructure for preprocessing, validation, normalization, source verification and safety. It must not be used to silently revert the current CV workflow to regex-first understanding or make AI profile construction depend on exact headings.

Personas are built later from the completed Professional Profile/Career Vault and are not generated during CV ingestion.

The authoritative evolution/runtime decision record is:

`docs/AI_TAKEOVER/07_ARCHITECTURE_EVOLUTION_AND_GLOBAL_INTELLIGENCE_RUNTIME.md`

## Global Intelligence runtime controls

The Global Intelligence Engine is the shared provider-neutral runtime for all AI workloads. The Project Control Intelligence surface must represent real runtime capabilities, not fake dashboard values.

### Task-based routing

Deterministic task/capability routing considers configured providers, health, priority, cost policy, quota and data classification. Application features do not choose vendors directly.

### Fallback routing

Fallback is ordered and policy-controlled. Retryable failures may trigger fallback. Every provider attempt is recorded, and the actual provider that produced the result must remain observable.

### Usage & cost controls

Every request should be attributable to tenant/user, feature, task, provider, model, latency, status and usage data where reported. CareerOS request limits are distinct from provider quota. Never fabricate token counts or costs.

### Health / latency / quota

Expose actual provider health, failures, fallback counts, latency and provider-reported quota/rate-limit information where available. Show explicit `No data`, `Not reported`, or `Unavailable` states when telemetry is not available.

## Database safety gate

Before and after every material database-affecting change, agents MUST follow:

- `docs/AI_TAKEOVER/06_DATABASE_SAFETY.md`
- `docs/DB_MIGRATION_AND_DATABASE_VALIDATION_PROCEDURE.md`
- `docs/DB_SCHEMA_BASELINE.md`
- `backend/scripts/validate_database.py`

Database migration validation is a release gate. Do not treat Docker startup failure as the first database validation step.

## Source-of-truth hierarchy

1. Actual source code + Git history
2. Actual runtime/test evidence
3. Current control-plane/handover records
4. Product requirements/specification
5. Historical conversation context

If these disagree, do not silently choose. Reconcile and record the discrepancy. When older architecture documentation conflicts with the current explicit architecture decision, use `docs/AI_TAKEOVER/07_ARCHITECTURE_EVOLUTION_AND_GLOBAL_INTELLIGENCE_RUNTIME.md` as the current decision record unless the Product Owner explicitly changes it.

## Current product order

Identity → Profile Builder → CV + Professional Document Vault → Profile Intelligence → Personas → Opportunity/Global Job Discovery → Email Intelligence → Company/Recruiter Intelligence → Job Intelligence/Matching → Skill Gap → Application Factory/CRM → Live Interview Assistant → Analytics/Learning → Global Mobility.

## Permanent rule

Every material AI session must leave a current handover record containing: branch, commit, objective, completed work, changed files, tests, runtime evidence, defects, blockers, decisions, risks, and exact next action.
