# CareerOS — Development Roadmap

## Development Model
Use:
`AGENTS.md` + relevant specification + one current task.

Complete one task, test it, review it, then move to the next.

## Phase 0 — Repository Reconciliation
Inspect current repository, compare against Specification/Blueprint, reconcile old assessment vs current code, no modifications.

## Phase 1 — Foundation Repair
Verify dependencies, Docker, PostgreSQL, pgvector, Alembic, frontend and backend builds.

## Phase 2 — Database Integrity
Reconcile models/migrations, relationships, indexes, ownership, evidence and vector-ready fields.

## Phase 3 — Authentication & Tenant Security
Registration, login, secure hashing, JWT, current-user, tenant context, RBAC and protected APIs.

## Phase 4 — Security Hardening
Exceptions, request IDs, logging, rate limiting, validation, secure uploads, SSRF/prompt-injection defenses.

## Phase 5 — Testing Foundation
pytest, pytest-asyncio, database/API/auth/tenant tests, CI, frontend build checks.

## Phase 6 — Career Vault
Career data CRUD, evidence, provenance and CV upload.

## Phase 7 — Persona Engine
Network Architect, Security Architect, Cyber Security Architect, Infrastructure Architect, Network Manager, IT Manager and Custom.

## Phase 8 — Job Intelligence
Manual JD import, normalization, dedupe, extraction, Job DNA and mandatory/preferred separation.

## Phase 9 — Career Ontology + Semantic Matching
Capability ontology, embeddings, retrieval, configurable scoring, hard failures and explanations.

## Phase 10 — pgvector
Vector infrastructure, provider abstraction, indexes, retrieval and caching/versioning.

## Phase 11 — Resume Studio + Truth Agent
JD-to-evidence, tailored resume, ATS alignment, truth validation and immutable versions.

## Phase 12 — Application Factory
Cover letter, answers, recruiter/hiring-manager messages and approval.

## Phase 13 — Application CRM
State machine, recruiter, interviews, offers, notes, reminders, versions and history.

## Phase 14 — Remote Intelligence
Worldwide vs restricted, timezone, work authorization, employment model, relocation and sponsorship.

## Phase 15 — Company + Interview Intelligence
Permitted company research, role context and evidence-backed interview preparation.

## Phase 16 — Global Mobility
Australia first, New Zealand next, then UAE, Qatar, Saudi Arabia, Singapore, UK, Canada and Germany/EU. Use official versioned rules.

## Phase 17 — Frontend
Dashboard, Career Vault, Personas, Jobs, Applications, Global Mobility, Interviews, Analytics, Settings. Use Lovable as visual reference; connect to real backend APIs.

## Phase 18 — Job Connectors
Start with manual import, permitted employer pages and generic feed/API framework. Add portals subject to their access conditions.

## Phase 19 — Analytics
Discovery, shortlist, applications, interviews, offers, acceptance, rejection by persona/source/country/salary/capability.

## Phase 20 — AI Orchestration & Cost
Provider abstraction, embeddings, cost tracking, caching, model routing and selective evidence retrieval.

## Phase 21 — Production Hardening
Logging, metrics, backups, security, Docker, Nginx, environment separation, performance and CI/CD.

## Phase 22 — SaaS Entitlements
Free, Pro, Global, Executive; server-side usage enforcement. Defer payment gateway until commercialization.

## Phase 23 — End-to-End Acceptance
User → Career Vault → Personas → JD → Job DNA → Match → Hard failures → Resume → Truth Agent → Application Package → Approval → CRM → Remote Fit → Migration Fit, plus tenant isolation, migrations, frontend build, backend tests and security tests.

## Operating Rule
Never mark a phase complete because code exists. It is complete only when the implementation works, relevant tests/builds pass and no known critical regression remains.
