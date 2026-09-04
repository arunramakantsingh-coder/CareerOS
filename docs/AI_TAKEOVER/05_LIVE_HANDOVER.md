# CareerOS — LIVE HANDOVER SNAPSHOT

> Update this file at the end of every material AI session. The goal is that a new AI can continue without access to prior chat.

## Snapshot

- Date: 2026-09-04
- Application development line: `working/m02-chatgpt-takeover-20260904`
- Parent implementation line: `working/m02-professional-identity-v1.5-20260904`
- Parent HEAD at takeover: `6e43b5c9dac6ee411bc43953f3d9d801d822ca1d`
- Active product release: v0.2 Global Job Intelligence
- Active milestone: M02 Profile Builder / Professional Identity reconciliation
- Overall status: **IMPLEMENTATION PRESENT / DATABASE RECONCILIATION + FULL RUNTIME QA IN PROGRESS**

## ChatGPT takeover

ChatGPT is now the engineering/QA continuation agent for the current M02 line. The previous coding AI's draft PR #16 remains unmerged. No release branch merge is authorized by this handover.

## Verified runtime defect

The local PostgreSQL database has no `alembic_version` table and is therefore not tracked by Alembic. The current application models expect `users.role`, but the local `users` table does not contain it. Normal password login and Google SSO both fail at the shared `User` query with PostgreSQL `UndefinedColumn: users.role does not exist`.

The database does already contain the three M02 tables `career_fact_evidence`, `persona_suggestions` and `email_connector_accounts` with the expected columns and foreign keys. The M02 `documents` columns and M02 indexes are missing. This is consistent with the old development startup path using SQLAlchemy `Base.metadata.create_all()` instead of Alembic migrations: `create_all()` creates missing tables but does not alter existing tables.

## Changes made by ChatGPT on takeover branch

- Removed development-time `Base.metadata.create_all(bind=engine)` from `backend/app/main.py` so application startup cannot silently bypass Alembic.
- Changed Docker backend startup to run `alembic upgrade head` before Uvicorn.
- Added `backend/scripts/reconcile_local_dev_db.py`, a one-time, explicit and re-runnable reconciliation utility for the known pre-Alembic local database. It adds only the missing 016 schema objects and establishes Alembic revision `016_m02_identity_intelligence` after verifying the required existing tables.
- Corrected M02 CI trigger scope so the workflow runs on `working/m02-*` pushes and PRs targeting `release/v0.2-global-job-intelligence`.

## Existing requirements still under active QA

Profile Builder, Career Passport, Profile Setup, multi-document intake, section-aware CV parsing, evidence graph, Career Vault, personas, developer reset/isolation, Gmail connector separation, themes, date controls, navigation separation, Bug Tracker/Project Tracker/Roadmap, security and regression tests remain subject to actual runtime verification.

## Non-negotiable safety

- Do not delete/recreate the PostgreSQL volume.
- Do not modify already-applied Alembic migrations.
- Do not manually patch Google Cloud OAuth configuration to hide an application/database defect.
- Do not merge PR #16 until local DB repair, CI, backend/frontend tests and browser journeys are verified.
- Never claim a test or runtime behavior passed unless it was actually executed.

## Exact next action

1. Pull `working/m02-chatgpt-takeover-20260904` locally.
2. Run the one-time database reconciliation utility.
3. Restart Docker Compose and verify Alembic reports `016_m02_identity_intelligence` as current.
4. Verify password login and Google SSO.
5. Run backend regression and frontend TypeScript gates.
6. Execute the M02 browser/runtime acceptance journey and fix every observed defect.
7. Update this handover with exact evidence and only then prepare a PR for human review.

## Handover marker

```text
[CAREEROS: CHATGPT ENGINEERING TAKEOVER — 2026-09-04]
Branch: working/m02-chatgpt-takeover-20260904
Parent: working/m02-professional-identity-v1.5-20260904 @ 6e43b5c
Release: v0.2 Global Job Intelligence
Milestone: M02 Professional Identity
Status: DB ROOT CAUSE IDENTIFIED / REPAIR CODE COMMITTED / FULL QA PENDING
PR #16: OPEN / DRAFT / NOT MERGED
```
