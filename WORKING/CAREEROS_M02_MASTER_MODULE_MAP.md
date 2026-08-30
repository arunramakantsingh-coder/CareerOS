# CareerOS v0.2 — M02 Master Module Map & Execution Control

Date: 2026-08-30
Status: ACTIVE — M02 ONLY

## Shared working rule
All M02 repair/implementation work occurs on `working/careeros-ai-sync-20260830` first. The release branch is protected. Every material action must be committed/pushed and reflected in `WORKING/`. DeepSeek proposes/implements; ChatGPT reviews code/scripts and integration; Arun executes approved runtime commands and supplies raw evidence; ChatGPT performs holistic QA and regression before M02 can be VERIFIED.

## M02 objective
Identity & Career Intake: Website → Sign Up/Sign In → Basic Account → Identity + Consent → CV Upload/Drag & Drop → Professional Document Vault → AI Profile Extraction Foundation → Candidate Profile → Explainable Profile Completeness → Profile Reconciliation foundation → Canonical Candidate Profile foundation.

## M02 phases

### M02-P1 Database/domain foundation
Executed DeepSeek model set:
- `backend/app/models/external_identity.py`
- `backend/app/models/candidate_profile.py`
- `backend/app/models/document.py`
- `backend/app/models/extraction_result.py`
- `backend/app/models/extraction_field.py`
- `backend/app/models/professional_experience.py`
- `backend/app/models/candidate_skill.py`
- `backend/app/models/candidate_certification.py`
- `backend/app/models/candidate_education.py`
- `backend/app/models/user.py` relationship changes
Migration: `backend/alembic/versions/014_m02_identity_career_intake.py`

### M02-P2 Authentication & identity APIs
- auth schemas/API/security/config
- `backend/app/main.py` router registration
Capabilities: register, login, `/auth/me`, external identity/consent foundation. No fake provider data.

### M02-P3 Candidate profile + document APIs
Expected executed API surface:
- `/api/v1/profile/`
- `/api/v1/profile/completeness`
- `/api/v1/profile/experiences`
- `/api/v1/profile/skills`
- `/api/v1/documents/upload`
- `/api/v1/documents/`
- `/api/v1/extraction/extract`

### M02-P4 AI Profile Extraction Foundation
Components: extraction schemas, CV parser/extractor, extraction service, `backend/app/api/extraction.py`.
Targets: personal/contact/location/preferences; employers/titles/dates/responsibilities/achievements/industries/projects/leadership; skills/technologies/networking/cybersecurity/architecture/cloud/infrastructure/security; certifications/education/degrees/training.
Mandatory trust states: EXTRACTED, INFERRED, USER-CONFIRMED, CONFLICTING, MISSING.

### M02-P5 Frontend authentication/entry
- `frontend/src/contexts/AuthContext.tsx`
- `frontend/src/app/login/page.tsx`
- `frontend/src/app/register/page.tsx`
- `frontend/src/app/onboarding/page.tsx`
- root layout/provider wiring

### M02-P6 CV upload + Professional Document Vault
- `frontend/src/components/documents/DocumentUpload.tsx`
- `frontend/src/app/documents/page.tsx`
Required UX: drag/drop, browse, truthful status, categories/subcategories, list/manage, extraction status, errors.

### M02-P7 Candidate profile + completeness
- `frontend/src/app/profile/page.tsx`
- `frontend/src/app/profile/experiences/page.tsx`
- `frontend/src/app/profile/skills/page.tsx`
Completeness must be explainable and separate from job-match score.

### M02-P8 Verification/regression/stability
- `scripts/test_m02.ps1`
Evidence must cover Git, DB/migration, backend routes, APIs, frontend build/start, browser-visible entry/auth, authenticated profile flow, document upload/persistence/refresh/extraction, negative/security cases, M01/v0.1 regression, cross-component traceability and stability.

## M02 acceptance IDs
M02-A01 entry/login/register visible
M02-A02 registration works
M02-A03 valid/invalid login behavior
M02-A04 session/auth/me/logout/protected routes
M02-A05 primary email/phone/LinkedIn states are honest
M02-A06 CV browse + drag/drop
M02-A07 uploaded bytes persist across request/refresh
M02-A08 vault list/manage own documents
M02-A09 extraction provenance
M02-A10 structured CV extraction
M02-A11 five-state trust model
M02-A12 candidate profile CRUD/persistence
M02-A13 completeness + explainable breakdown
M02-A14 experiences/skills CRUD
M02-A15 tenant/user isolation
M02-A16 negative/error/security paths
M02-A17 frontend/backend route and schema alignment
M02-A18 DB/migration integrity
M02-A19 M01/v0.1 regression
M02-A20 stability/repeatability

## Current known reconstruction blockers
1. Documents UI expected list/delete routes that were absent from the inspected backend router state.
2. Document upload created metadata/path but did not persist uploaded bytes.
3. ZIP/content validation and untrusted-file handling need review.
4. Multi-upload response/UI shape can create incomplete or duplicate records.
5. Upload progress was not tied to actual transfer progress.
6. `main.py` compatibility changes require regression verification.
7. Current UI has fallen back to an older shell/entry experience; restore from intended M02 implementation and verify layout/routes rather than guessing.

## Module isolation requirement
Every change must declare milestone, module, submodule/phase, backend files, frontend files, DB migration, tests/evidence, dependencies touched and regression surface. Unrelated modules must not be modified. Dependencies outside M02 require a documented decision before implementation.

## Completion rule
Only when all M02 acceptance IDs pass, raw runtime evidence exists, regression/stability pass, and registry history is updated may ChatGPT issue `[CAREEROS: M02 — VERIFIED]`. M03+ remain NOT AUTHORIZED until then.
