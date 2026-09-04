# CareerOS — Current Control State

## Roles
Developer: ChatGPT takeover lead + coding agents under instruction
Lead Architect / QA / Release Gate: ChatGPT
Runtime / Evidence / UI Acceptance: Arun

## Current State
M02 Professional Identity Intelligence is under active engineering repair and acceptance. The previous coding AI's implementation remains available for comparison, but its completion claims are not treated as acceptance evidence.

**No merge to `release/v0.2-global-job-intelligence` until ChatGPT explicitly authorizes the M02 release gate.**

## Active Working Branch
`working/m02-chatgpt-takeover-20260904`

The takeover branch continues from the previous coder's verified HEAD `6e43b5c9dac6ee411bc43953f3d9d801d822ca1d` and contains subsequent ChatGPT-controlled fixes.

## Engineering Handoff
The persistent workflow is defined in `docs/29_CHATGPT_ENGINEERING_HANDOFF_PROTOCOL.md`. Any future AI must follow that document before changing code.

## Immediate Sequence
1. Foundation stability and migration reconciliation
2. Authentication and OAuth regression
3. Career Vault/CV
4. Personas
5. Evidence Library and provenance
6. Developer Mode/security
7. Full M02 browser/runtime journey
8. M02 acceptance gate
9. Only then authorize the next milestone

## Current Critical Defect
The local PostgreSQL database had no `alembic_version` table and represented only a partial application of migration 016. `users.role` and the five M02 document columns were missing while the three M02 tables and their foreign keys already existed. This broke both normal login and Google Sign-In because the ORM queried `users.role`.

A narrowly scoped transactional legacy reconciliation utility was added. Fresh databases remain on the normal Alembic path; the known legacy partial-M02 state is reconciled before `alembic upgrade head` runs.

## Runtime
Every milestone must leave a locally usable system. Minimum checks:
- http://localhost:3000
- http://localhost:8000/api/v1/health
- feature-specific UI/API tests
- database migration state
- authentication regression

## Verification Standard
A claim is not acceptance evidence unless it is backed by one or more of:
- CODE VERIFIED
- TEST VERIFIED
- CI VERIFIED
- RUNTIME VERIFIED

The final milestone status is **ACCEPTED** only when all required layers pass.

## Freeze
Do not move to the next milestone until ChatGPT issues explicit authorization.
