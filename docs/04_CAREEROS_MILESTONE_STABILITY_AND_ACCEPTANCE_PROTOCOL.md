# CareerOS — Milestone Stability & Acceptance Protocol

## Non-Negotiable
A milestone is not complete because an AI says it is complete.

## Pipeline
```text
Milestone Brief
 ↓
Architect Approval
 ↓
Developer Implementation
 ↓
Developer Tests
 ↓
Actual Runtime Execution
 ↓
Evidence Package
 ↓
GitHub Review
 ↓
QA Review
 ↓
Human Runtime/UI Acceptance
 ↓
Stability Gate
 ↓
MILESTONE VERIFIED
 ↓
Next Milestone Brief
```

## Evidence Integrity
A script is not evidence. An expected result is not evidence. DeepSeek must never pre-generate runtime results.

## DeepSeek Closeout Must Include
- milestone/scope
- acceptance criteria
- files changed
- DB/API/frontend changes
- commands actually executed
- actual outputs
- runtime URLs
- tests
- security observations
- known issues
- regression results
- commit SHA
- proposed next milestone (proposal only)

## Stability Gate
Every milestone must execute, as applicable:
```powershell
docker compose ps
Invoke-WebRequest http://localhost:8000/api/v1/health
Invoke-WebRequest http://localhost:3000/
Test-NetConnection localhost -Port 8000
Test-NetConnection localhost -Port 3000
docker compose logs backend --tail=30
docker compose logs frontend --tail=30
```
Plus module-specific tests, UI tests and regressions.

## Status Definitions
IMPLEMENTED = code exists.
TESTED = tests actually executed.
QA VERIFIED = ChatGPT reviewed actual evidence.
RUNTIME ACCEPTED = Arun confirmed local runtime/UI.
MILESTONE VERIFIED = all required gates passed.

Only MILESTONE VERIFIED permits the next milestone.

## Failure Rule
Blocking `FAIL > 0` or required `PENDING > 0` keeps the milestone open.

A defect in a later/deferred module must not block the current milestone unless explicitly required by that milestone.
