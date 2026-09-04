# CareerOS — ChatGPT Engineering Handoff Protocol

## Purpose

This document is the persistent operating contract for any AI that takes over CareerOS engineering work. It prevents loss of project context when the coding AI changes.

## Authority

- Arun: product owner, local runtime operator, browser/UI acceptance.
- ChatGPT: lead architect, engineering lead, QA authority, release gate.
- Coding AI/agents: implementation execution under the active branch and milestone scope.
- No AI may merge a milestone into the frozen release branch without explicit release authorization.

## Source of truth order

1. Current GitHub branch and commit.
2. Repository architecture and migration files.
3. This protocol and `docs/22_CAREEROS_CURRENT_CONTROL_STATE.md`.
4. Milestone/product requirements in the repository docs.
5. Local runtime evidence supplied by Arun.
6. Prior AI claims are evidence only when backed by code, tests, CI, or runtime verification.

## Required workflow from day one

### Phase 0 — Takeover and baseline

1. Identify the target release branch and active working branch.
2. Record local/remote HEAD and worktree state.
3. Inspect current PRs and recent commits.
4. Read the control-state, handoff, product-scope, architecture, milestone, and relevant QA documents.
5. Establish the runtime baseline: Docker, PostgreSQL, backend, frontend, migrations, routes, authentication, and existing tests.
6. Never assume a previous AI's completion claim is correct.

### Phase 1 — Diagnose

1. Reproduce each reported defect.
2. Determine whether the failure is frontend, API, domain, database, configuration, OAuth, security, or integration.
3. Prefer repository evidence and runtime logs over speculation.
4. Do not modify production/release branches while diagnosing.
5. Do not destroy databases or bypass migrations to make a test pass.

### Phase 2 — Fix

1. Fix the root cause, not only the visible symptom.
2. Preserve existing user/data unless destructive behavior is explicitly required.
3. Use Alembic for schema evolution; never silently rely on `Base.metadata.create_all()` for application upgrades.
4. Keep OAuth providers/configuration unchanged unless the evidence proves the provider configuration is wrong.
5. Add or update regression tests for every fixed defect.
6. Update documentation/control state when architecture or operating procedure changes.

### Phase 3 — Verify

Every feature must pass all applicable layers:

- static/compile checks
- unit tests
- API tests
- database/migration checks
- frontend TypeScript/build checks
- Docker startup checks
- browser/runtime journey
- security/tenant-isolation checks

A feature is not complete because code exists. It is complete only when the required verification evidence passes.

### Phase 4 — Release candidate

1. Confirm working tree is clean.
2. Confirm local and remote commit SHA.
3. Confirm CI status.
4. Confirm runtime baseline.
5. Confirm milestone acceptance checklist has no unresolved blocker.
6. Prepare exact local pull/switch/rebuild/test instructions for Arun.
7. Do not merge into `release/v0.2-global-job-intelligence` until explicit authorization.

## Local handoff command standard

When a working branch is ready for Arun, provide one copy/paste-safe PowerShell block containing:

- `cd` to the repository root
- `git status --short --branch`
- `git fetch origin --prune`
- safe branch creation/switch instructions that do not overwrite an older branch
- `git log -1 --oneline`
- Docker rebuild/start commands
- backend compile check
- frontend TypeScript check
- API health check
- exact browser URL(s)
- expected branch/commit and expected verification results

Do not ask Arun to paste Markdown fences into PowerShell. Commands must be presented as raw commands inside the supported writing block.

## Evidence rule

Use these labels consistently:

- **CODE VERIFIED** — implementation inspected in GitHub.
- **TEST VERIFIED** — automated test passed.
- **CI VERIFIED** — GitHub CI passed.
- **RUNTIME VERIFIED** — local Docker/API/browser evidence passed.
- **ACCEPTED** — all required evidence exists and the milestone gate is explicitly approved.

## Database safety rule

Never use database deletion, volume destruction, blind `alembic stamp`, or manual schema changes as a first response to migration drift. First reconstruct the actual schema and migration state. Any reconciliation utility must be narrowly scoped, idempotent, transactional, and safe for the known legacy state.

## Milestone rule

The active milestone remains frozen until its acceptance gate passes. Fixing a defect within the current milestone is authorized engineering work; starting the next product milestone is not authorized without explicit release-gate approval.
