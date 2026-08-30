# CareerOS — ChatGPT / DeepSeek Shared Working Memory

Last synchronized: 2026-08-30

## Roles
- Product Owner / runtime evidence / UI acceptance: Arun
- Developer / implementation engineer: DeepSeek
- Lead architect / QA / verification / release gate: ChatGPT

## Control protocol
DeepSeek proposes/implements only the explicitly authorized milestone. ChatGPT reviews code and scripts before execution/authorization. Arun executes runtime commands and supplies raw evidence. ChatGPT performs QA and issues VERIFIED / NOT VERIFIED. No next milestone is authorized until the current milestone passes its acceptance and stability gate.

## Product direction
IDENTITY → CAREER DOCUMENTS → AI PROFILE → PROFILE RECONCILIATION → PERSONAS → GLOBAL JOB DISCOVERY → EMAIL/RECRUITER INTELLIGENCE → JOB INTELLIGENCE → MATCHING → SKILL GAPS → APPLICATION ASSISTANCE → APPLICATION CRM → REMOTE INTELLIGENCE → INTERVIEW/LIVE INTERVIEW → ANALYTICS/LEARNING.

Global Mobility is deliberately later.

Document-first onboarding is locked. Professional documents are evidence storage and AI Profile input. Extracted facts require provenance and must never be fabricated. Trust states: EXTRACTED, INFERRED, USER-CONFIRMED, CONFLICTING, MISSING.

## Milestones
M01 Foundation / Stabilization — VERIFIED in existing project record.
M02 Identity + Career Intake — implementation exists, but ChatGPT has NOT declared it verified.
M03+ — NOT AUTHORIZED.

## Current release checkpoint
Release branch: `release/v0.2-global-job-intelligence`
Release tip: `62ba25c38efb87dbdef2efbcd3bd3a44c08eded0`
Shared working branch: `working/careeros-ai-sync-20260830`

## Current audit findings
1. Documents UI calls GET `/api/v1/documents/` and DELETE `/api/v1/documents/{id}`, but backend currently exposes only upload endpoints. This is a contract blocker.
2. Document upload creates metadata/storage paths but does not persist actual bytes. The vault is therefore not yet a functioning persistent evidence store.
3. ZIP ingestion is in-memory/metadata-only and needs stronger path/content validation before acceptance.
4. File validation is extension/size based; magic-byte/content validation and malware scanning are absent.
5. Multi-upload response shape does not match the full `Document` UI shape and the component may trigger duplicate callbacks.
6. Upload progress is cosmetic.
7. Local `main.py` mounts `v01_product`, apparently restoring v0.1 compatibility routes; this requires regression evidence.
8. CORS is currently permissive; production hardening is follow-up unless needed for M02.
9. Module registry wording about M02 authorization is stale relative to the locked M02 brief; reconcile explicitly after QA rather than silently rewriting history.

## Working rule
Do not reset the local project wholesale. Preserve the five meaningful semantic local changes and discard only line-ending-only churn. Repair blockers minimally. Keep release branch unchanged until QA passes.

## Next action
DeepSeek: inspect the shared working branch and audit, then propose a minimal repair plan. Do not claim verification and do not execute out-of-scope work.

ChatGPT: review every DeepSeek script/code proposal before Arun runs it.

Arun: execute only approved commands and return raw output.
