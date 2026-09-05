# CareerOS — LIVE HANDOVER SNAPSHOT

> Update this file at the end of every material AI session. The goal is that a new AI can continue without access to prior chat.

## Snapshot

- Date: 2026-09-05
- Application development line: `working/m02-professional-identity-v1.6-reconciled-20260905`
- Application HEAD at this handover update: `cf0ae51bda6d392dd7afdb4c47ba2c23ca3eecb2`
- Active product release: v0.2 Global Job Intelligence
- Active milestone: **M02 Professional Identity / Profile Builder / Career Intake**
- Current integration PR: **#19 — M02 v1.6 Reconciled Professional Identity implementation**
- Release target: `release/v0.2-global-job-intelligence`
- Overall status: **IMPLEMENTATION PRESENT / LOCAL RUNTIME & E2E ACCEPTANCE PENDING**

## Current development model

CareerOS uses an AI-led, GitHub-first development loop:

```text
User + Lead AI discuss requirement
        ↓
Lead AI defines scope + acceptance criteria
        ↓
Coding AI implements directly on authorized GitHub working branch
        ↓
Tests / migrations / code validation
        ↓
Commit + exact implementation report
        ↓
Lead AI reviews GitHub state
        ↓
Human pulls exact branch and runs local Docker/browser acceptance
        ↓
Human returns runtime evidence
        ↓
Lead AI diagnoses / coding AI fixes if required
        ↓
Final QA / release review
        ↓
VERIFIED only after evidence + approval
```

The human is the local runtime/operator and product owner, not the normal source-file editor. The coding AI should use GitHub write access when available and then hand the human a precise, reproducible local test procedure.

## Required local-testing handoff

After a GitHub implementation, the AI must provide:

- exact branch;
- expected commit SHA;
- pull/checkout commands;
- Docker rebuild/start commands;
- migration/database commands when applicable;
- browser/API routes;
- expected results;
- regression/negative checks;
- destructive commands to avoid;
- exact logs/screenshots/output to return on failure.

For database changes, preserve the PostgreSQL volume unless destructive reset is explicitly authorized.

## Current M02 state

M02 v1.6 is the reconciled continuation of the Professional Identity work on top of the auth-tested v0.2 baseline. The implementation includes the profile/evidence/document-intelligence foundations described by PR #19. Code-level validation has been performed on the branch, but **local Docker/browser runtime acceptance remains the gate**.

The latest previously reported migration work establishes a controlled Alembic synchronization path rather than relying on `Base.metadata.create_all()` during application startup. The local database migration must be observed in the user's environment before authentication/database regression can be considered runtime-verified.

## Important release safety

- v0.1 remains frozen.
- `release/v0.2-global-job-intelligence` must not be changed as part of normal M02 implementation.
- PR #19 must not be merged automatically.
- Do not claim M02 `VERIFIED` before local runtime evidence and final QA/release review.
- Do not start Global Job Discovery merely because profile code exists; complete the M02 acceptance gate first.
- Live Interview remains a divergent/legacy line and requires explicit reconciliation before integration.

## Takeover requirements

A new AI must first read:

1. `AI_TAKEOVER.md`
2. `AGENTS.md`
3. `docs/AI_TAKEOVER/05_LIVE_HANDOVER.md`
4. `docs/21_AI_TO_AI_COORDINATION_PROTOCOL.md`
5. `docs/22_CAREEROS_CURRENT_CONTROL_STATE.md`
6. `docs/23_CAREEROS_MODULE_VERSION_REGISTRY.md`
7. relevant product/spec/domain documents

Then inspect actual GitHub branches, HEAD, ancestry, PRs, migrations, tests and current implementation. Do not trust stale documentation when GitHub/runtime evidence disagrees; record the discrepancy.

## Closeout template

Every material AI session must leave:

```text
Timestamp:
Active branch:
Commit SHA:
Milestone/module/version:
Objective:
Implementation completed:
Files changed:
Database/migrations:
APIs:
UI:
Tests actually executed:
CI status actually observed:
Local runtime evidence:
Known bugs:
Blockers/external dependencies:
Material decisions:
What is NOT complete:
Exact next action:
```

## Handover marker

```text
[CAREEROS: AI HANDOVER — 2026-09-05]
Application branch: working/m02-professional-identity-v1.6-reconciled-20260905
Control state: M02 v1.6 IMPLEMENTATION PRESENT / LOCAL RUNTIME E2E ACCEPTANCE PENDING
Release branch: release/v0.2-global-job-intelligence
Current PR: #19
Latest control-plane commit: cf0ae51bda6d392dd7afdb4c47ba2c23ca3eecb2
No M02 VERIFIED claim has been made by this handover update.
```
