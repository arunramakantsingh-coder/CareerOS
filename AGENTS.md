# CareerOS AI Development Rules

## Purpose
CareerOS is an AI-Powered Global Career Operating System. It is an existing codebase. AI coding agents must extend and repair the current implementation rather than rebuild the project.

## Authoritative Documents
Read these before architectural changes:
- `docs/CAREEROS_SPEC.md`
- `docs/CAREEROS_BLUEPRINT.md`
- `docs/CAREEROS_PROJECT_ASSESSMENT.md`
- `docs/DEVELOPMENT_ROADMAP.md`

The current repository is authoritative for what already exists. The Specification and Blueprint are authoritative for intended product behavior.

## Core Principle
CareerOS is **career-centric, not job-title-centric**.

Career Vault is the source of truth. Jobs become Job DNA. Matching occurs at capability/evidence level.

## Non-Negotiable Rules
1. Do not rebuild the application from scratch.
2. Do not delete working functionality without explaining why.
3. Inspect existing code before changing a subsystem.
4. Prefer minimal, modular changes.
5. Do not introduce a new framework without justification.
6. Never modify an already-applied Alembic migration; create a new migration.
7. Never commit secrets, tokens, passwords or private keys.
8. Never trust client-supplied `tenant_id`.
9. User-owned data must be tenant-scoped and authorization-checked.
10. Never fabricate career facts, job facts or immigration rules.
11. Never claim tests passed unless actually executed.
12. Do not implement unauthorized job scraping or account automation.
13. Application submission must remain human-approved where automation is restricted.
14. Do not hard-code immigration rules inside prompts.
15. Keep AI providers behind replaceable service interfaces.
16. Retrieve only relevant Career Vault evidence for AI calls.
17. Do not keyword-stuff resumes.
18. Every material generated career claim must map to Career Vault evidence.

## Career Data
AI may rewrite, summarize, prioritize, reorder and tailor verified information. It may not invent employers, dates, technologies, certifications, projects, achievements, metrics or experience.

## Job Intelligence
Evaluate title, role family, responsibilities, capabilities, technologies, architecture domains, security, leadership, governance, industry, seniority, transferable skills, location, employment model, salary, remote and migration constraints.

A job can be relevant even when its title does not resemble the user's persona title.

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

Mandatory failures are evaluated separately. A high semantic score must not hide a hard disqualifier.

## Truth Agent
The Truth & Compliance Agent is a mandatory gate before an application package becomes `READY_FOR_REVIEW`. Validate dates, employers, projects, technologies, certifications, metrics, years of experience and material claims. Unsupported claims are removed or flagged.

## Migration
Migration information is informational, not legal advice. Rules must be structured and versioned with country, visa, rule key/value, effective dates, official source and verification date. Australia and New Zealand are priority markets.

## Job Sources
Prefer APIs, partner feeds, RSS/alerts, permitted integrations and public employer career pages. Do not implement unauthorized scraping or account automation.

## Development Workflow
For every task:
1. Read `AGENTS.md`.
2. Read the relevant specification section.
3. Inspect the existing implementation.
4. State the intended change.
5. Make the smallest safe change.
6. Run relevant tests/builds.
7. Fix failures.
8. Report changed files.
9. Report tests actually executed.
10. Stop at the requested task.

## Git
Before major changes inspect `git status` and preserve a clean checkpoint. Never overwrite another developer's uncommitted work without explicit instruction.

## Frontend
Use the existing Next.js/TypeScript/Tailwind architecture unless a documented reason requires change. Build reusable components and connect them to real APIs.

## Backend
Keep routes, schemas, services, models/repositories and AI integrations logically separated. Avoid putting domain logic directly in route handlers when a service layer is appropriate.

## AI Cost
Prefer deterministic logic, then embeddings/retrieval, then lightweight models, then stronger models only where needed. Cache repeatable analysis safely. Track AI usage and estimated cost.

## Completion
A task is complete only when implementation exists, the app still starts, relevant tests/builds pass, and no known critical regression remains.
