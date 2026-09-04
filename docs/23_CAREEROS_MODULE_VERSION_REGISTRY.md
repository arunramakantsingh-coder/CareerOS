# CareerOS — Module / Phase / Version Registry
Version: 1.0
Status: AUTHORITATIVE CONTROL RECORD
Purpose: Permanent historical and maintenance record for every CareerOS module.

## 1. Why this document is mandatory

This registry is the permanent record of:

- product stage
- release/version
- milestone
- module
- implementation scope
- database migrations
- API/UI components
- tests
- verification status
- Git commit
- defects/fixes
- architectural decisions
- deferred work

Future enhancement, refactoring and bug-fix work MUST consult this registry before changing an existing module.

Do not delete historical entries. Add a new versioned entry.

## 2. Version hierarchy

```text
PRODUCT
  CareerOS

RELEASE
  v0.1 — Personal Job & Interview Copilot
  v0.2 — Global Job Intelligence
  v0.3 — Global Mobility
  v1+  — SaaS / Advanced Automation

STAGE
  S01 Identity
  S02 Career Intelligence
  S03 Personas
  S04 Global Discovery
  S05 Email Intelligence
  S06 Company/Recruiter Intelligence
  S07 Job Intelligence & Matching
  S08 Skill Gap Intelligence
  S09 Application Factory
  S10 Application CRM
  S11 Remote Intelligence
  S12 Interview Intelligence
  S13 Analytics/Learning
  S14 Global Mobility
  S15 Production/SaaS

MILESTONE
  M01, M02, M03 ... within the active release

MODULE VERSION
  e.g. AUTH-1.0, VAULT-1.0, PERSONA-1.0, MATCH-1.0
```

## 3. Immutable history rule

A completed/verified record is historical.

If a module changes:

```text
Existing version → preserve
New implementation → new module version
New milestone → new milestone record
New verification → new evidence record
```

Never rewrite history to make an old implementation appear to have contained a later feature.

## 4. Required record fields

Every module version record must contain:

| Field | Required |
|---|---|
| Release | YES |
| Stage | YES |
| Milestone | YES |
| Module ID | YES |
| Module Version | YES |
| Scope | YES |
| Dependencies | YES |
| DB/Migration IDs | Where applicable |
| API routes | Where applicable |
| UI routes/components | Where applicable |
| Tests | YES |
| Security checks | Where applicable |
| Runtime evidence | YES before VERIFIED |
| Git commit | YES before VERIFIED |
| QA decision | YES |
| Status | YES |
| Known limitations | YES |
| Deferred items | Where applicable |

## 5. Status vocabulary

```text
PLANNED
AUTHORIZED
IMPLEMENTING
IMPLEMENTED
EXECUTED
OBSERVED
QA REVIEW
VERIFIED
DEFERRED
SUPERSEDED
RETIRED
```

`VERIFIED` may only be issued by ChatGPT after the required evidence and acceptance criteria are satisfied.

## 6. Current v0.2 stage register

| Stage | Module | Current intent |
|---|---|---|
| S01 | Identity & Onboarding | Account, providers, identity linking, consent |
| S02 | Career Vault / AI Profile | CV + professional-document ingestion and profile extraction |
| S03 | Persona Engine | Dynamic evidence-based personas |
| S04 | Global Job Discovery | Portals, employer sites, permitted feeds |
| S05 | Email Intelligence | Authorized mailbox/job/recruiter intelligence |
| S06 | Company/Recruiter Intelligence | Employer/recruiter resolution |
| S07 | Job Intelligence & Matching | Job normalization, Job DNA, capability matching |
| S08 | Skill Gap Intelligence | 60% signal, gap persistence and cumulative analysis |
| S09 | Application Factory | Tailored materials and human approval |
| S10 | Application CRM | Application lifecycle and outcome tracking |
| S11 | Remote Intelligence | Remote/location/work authorization intelligence |
| S12 | Interview Intelligence | Preparation + live interview assistance |
| S13 | Analytics/Learning | Market and outcome learning |
| S14 | Global Mobility | Visa/sponsorship/relocation |
| S15 | Production/SaaS | Advanced automation, hardening, monetization |

## 7. Current milestone record

### M01 — Foundation / Stabilization
Status: VERIFIED according to the current control state supplied by Arun/QA.

### M02 — Identity & Career Intake
Status: IMPLEMENTING — explicit Product Owner authorization received for the Profile Intelligence v1.0 slice.

Scope:
- public CareerOS entry
- sign-up/sign-in
- email/password
- OAuth/OIDC provider architecture
- phone verification/OTP
- WhatsApp verification as an optional verification/communication channel
- identity linking
- consent
- session/protected routes
- initial onboarding
- CV upload/drag-drop
- professional document vault intake
- document provenance
- AI extraction pipeline foundation
- candidate profile prefill
- profile completeness calculation/display

M02 does NOT include:
- full global job connector implementation
- migration/visa intelligence
- autonomous application submission
- production SaaS monetization

### M02-S02 / PROFILE-INTELLIGENCE-1.0 — RC1 / IMPLEMENTING
Branch: `integration/m02-profile-intelligence-v1.0`
Feature lineage: `feature/m02-profile-intelligence-v1.0`
Base commit: `1da1670`
Integration commit: `b7c07b5` (latest functional ingestion hardening)

Scope:
- Google OIDC sign-in
- Gmail external authorization foundation
- LinkedIn OIDC sign-in and profile sync foundation
- multi-file / drag-drop / folder / ZIP / camera document intake
- safe ZIP extraction including uncompressed expansion cap
- PDF/DOC/DOCX/TXT/image parsing and OCR fallback
- document hashing, classification and canonical naming
- persistent development evidence storage
- extraction into existing canonical CandidateProfile child models
- provenance and evidence-backed Profile Intelligence UI
- browser-hostname API resolution for LAN/mobile access
- LAN CORS support for private browser origins

Database migration IDs:
- Reuses existing M02 migrations 014 and 015; no new migration in this slice.

API:
- `POST /api/v1/documents/batch-upload`
- `GET /api/v1/profile/intelligence`
- `GET /api/v1/auth/oauth/google/start`
- `POST /api/v1/auth/oauth/google/gmail/authorize-url`
- `GET /api/v1/auth/oauth/google/callback`
- `GET /api/v1/auth/oauth/linkedin/start`
- `GET /api/v1/auth/oauth/linkedin/callback`
- `POST /api/v1/auth/oauth/linkedin/sync-profile`

UI:
- `/documents`
- `/profile/intelligence`
- login Google/LinkedIn buttons
- multi-file/folder/camera uploader
- existing single-file uploader/extractor retained

Status: IMPLEMENTING / RC1
Verification: PENDING local runtime evidence
Known limitations: LinkedIn self-serve OIDC does not provide an arbitrary downloadable member CV; deeper profile fields depend on LinkedIn-approved API access. Full conflict-review UI remains a follow-on profile slice.

## 8. Evidence record template

```text
Module ID:
Module Version:
Release:
Stage:
Milestone:
Scope:
Implementation Commit:
Migration:
API:
UI:
Tests:
Runtime Evidence:
Security Evidence:
QA Decision:
Status:
Known Limitations:
Deferred:
Supersedes:
```

## 9. Maintenance rule

Before modifying a module:

1. Locate the latest registry entry.
2. Read its scope and known limitations.
3. Identify the Git commit/version.
4. Determine whether the requested change is:
   - bug fix
   - enhancement
   - refactor
   - new capability
5. Create a new module version record.
6. Preserve backward compatibility where required.
7. Update tests and documentation.
8. Record verification evidence.

This registry is a permanent engineering record, not a disposable milestone note.
