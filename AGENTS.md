# CareerOS AI Development Rules

## FIRST-READ HANDOVER

Before making changes, read `AI_TAKEOVER.md`. The default branch is a repository entrypoint, not necessarily the active development branch. The 2026-09-03 active v0.2 development line is `working/m02-profile-builder-v1.3-20260902` @ `a3dc548`.

Then read the current handover files under `docs/AI_TAKEOVER/` on that active branch, followed by `docs/21_AI_TO_AI_COORDINATION_PROTOCOL.md`, `docs/22_CAREEROS_CURRENT_CONTROL_STATE.md`, and `docs/23_CAREEROS_MODULE_VERSION_REGISTRY.md`.

The profile-builder line is the current product continuation. `working/live-interview-workspace-v0.2.2-20260902` is a known diverged older working line and must not be treated as the next version without reconciliation.

## Purpose
CareerOS is an AI-Powered Global Career Operating System. It is an existing codebase. AI coding agents must extend and repair the current implementation rather than rebuild the project.

## Authoritative Documents
Read these before architectural changes:
- `AI_TAKEOVER.md`
- `docs/AI_TAKEOVER/01_PROJECT_REQUIREMENTS_BASELINE.md`
- `docs/AI_TAKEOVER/02_CURRENT_STATE_20260903.md`
- `docs/AI_TAKEOVER/03_GIT_BRANCH_AND_RELEASE_CONTROL.md`
- `docs/AI_TAKEOVER/05_LIVE_HANDOVER.md`
- `docs/CAREEROS_SPEC.md`
- `docs/CAREEROS_BLUEPRINT.md`
- `docs/CAREEROS_PROJECT_ASSESSMENT.md`
- `docs/DEVELOPMENT_ROADMAP.md`
- `docs/21_AI_TO_AI_COORDINATION_PROTOCOL.md`
- `docs/22_CAREEROS_CURRENT_CONTROL_STATE.md`
- `docs/23_CAREEROS_MODULE_VERSION_REGISTRY.md`

Current repository implementation and actual runtime evidence are authoritative for what exists. Product/spec documents define intended behavior. Historical documents are context, not permission to overwrite newer Git/runtime facts.

## Product Direction

```text
CareerOS
  v0.1 Personal Job & Interview Copilot  <- FROZEN
  v0.2 Global Job Intelligence           <- CURRENT
  v0.3 Global Mobility
  v1/v2 SaaS
```

Current v0.2 sequence:

```text
Authentication / Identity
→ Profile Builder
→ CV + Professional Document Vault
→ Profile Intelligence
→ Personas
→ Global Job Discovery
→ Email Intelligence
→ Company / Recruiter Intelligence
→ Job Intelligence + Matching
→ Skill Gap Intelligence
→ Application Factory + CRM
→ Live Interview Assistant
→ Analytics / Learning
→ Global Mobility
```

## Core Principle
CareerOS is **career-centric, not job-title-centric**.

Career Vault/evidence is the source of truth for factual career information. Jobs become Job DNA. Matching occurs at capability/evidence level.

## Non-Negotiable Rules
1. Do not rebuild the application from scratch.
2. Do not delete working functionality without explaining why.
3. Inspect existing code before changing a subsystem.
4. Prefer minimal, modular, reversible changes.
5. Do not introduce a new framework without justification.
6. Never modify an already-applied Alembic migration; create a new migration.
7. Never commit secrets, tokens, passwords, OAuth client secrets or private keys.
8. Never trust client-supplied `tenant_id`.
9. User-owned data must be tenant-scoped and authorization-checked.
10. Never fabricate career facts, job facts, company facts or immigration rules.
11. Never claim tests passed unless actually executed.
12. Do not implement unauthorized job scraping or account automation.
13. Application submission must remain human-approved where automation is restricted.
14. Keep AI providers behind replaceable service interfaces.
15. Retrieve only relevant Career Vault evidence for AI calls.
16. Do not keyword-stuff resumes.
17. Every material generated career claim must map to evidence.
18. Mandatory job requirements are evaluated separately from semantic score.
19. A high semantic score must not hide a hard disqualifier.
20. Do not silently change product scope or milestone boundaries.
21. Stop when the requested task is complete; do not perform unrelated cleanup.

## Career Data
AI may rewrite, summarize, prioritize, reorder and tailor verified information. It may not invent employers, dates, technologies, certifications, projects, achievements, metrics or experience. Generated claims must be traceable to evidence.

## Job Intelligence
Evaluate title, role family, responsibilities, capabilities, technologies, architecture domains, security, leadership, governance, industry, seniority, transferable skills, location, employment model, salary, remote and migration constraints.

Prefer APIs, partner feeds, RSS/alerts, permitted integrations and public employer career pages. Respect terms of service and automation restrictions.

## Matching
Initial configurable weights:
- Technical/capability 25%
- Relevant experience 20%
- Architecture/domain 15%
- Leadership/seniority 10%
- Industry/domain 10%
- Location/remote 5%
- Salary 5%
- Migration/relocation 5%
- Certification/qualification 5%

Mandatory failures are evaluated separately.

## Truth Agent
Truth & Compliance is a mandatory gate before an application package becomes `READY_FOR_REVIEW`. Validate material claims against Career Vault evidence.

## Migration
Migration information is informational, not legal advice. Rules must be structured/versioned with country, visa/rule key/value, effective dates, official source and verification date.

## Development Workflow
For every task:
1. Read the first-read handover and relevant control-plane docs.
2. Inspect the actual branch, ancestry and implementation.
3. State the intended change and non-goals.
4. Make the smallest safe change.
5. Run relevant tests/builds/runtime checks.
6. Fix failures.
7. Report exact changed files and actual evidence.
8. Update the live handover record.
9. Stop at the requested task/milestone.

## Git
Before major changes inspect branch, status, HEAD and ahead/behind state. Create a versioned backup before risky changes. Never overwrite another developer's uncommitted work. Never merge a PR without the required owner/reviewer approval.

## Frontend
Use the existing Next.js/TypeScript/Tailwind architecture unless a documented reason requires change. Build reusable components and connect them to real APIs. Keep navigation domain-level vertically and contextual horizontally.

## Backend
Keep routes, schemas, services, models/repositories and AI integrations logically separated. Avoid putting domain logic directly in route handlers when a service layer is appropriate.

## AI Cost
Prefer deterministic logic, then retrieval/embeddings, then lightweight models, then stronger models only where needed. Cache repeatable analysis safely and track AI usage/cost.

## Completion
A task is complete only when implementation exists, the app still starts, relevant tests/builds pass, no known critical regression remains, GitHub reflects the change, and the persistent handover reflects the new state.
