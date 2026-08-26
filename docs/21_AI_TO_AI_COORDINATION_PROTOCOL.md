# CareerOS — AI-to-AI Coordination Protocol
Version: Reconciled

## Participants
- ChatGPT — Lead Architect / QA / Security / Verification Authority
- DeepSeek — Developer / Coder
- Arun — Human Execution / Runtime / Evidence Bridge / UI Acceptance

## Canonical Truth
1. GitHub = implementation truth.
2. Approved docs = product/architecture intent.
3. Actual local execution = runtime truth.
4. Arun's browser/runtime observation = human acceptance truth.

## Communication
```text
ChatGPT → approved milestone brief → DeepSeek
DeepSeek → implementation + executable evidence commands → Arun
Arun → actual outputs/UI observations → ChatGPT
ChatGPT → VERIFIED / NOT VERIFIED → project control
```

## Critical Rule
DeepSeek's report is not QA approval. A planned command is not runtime evidence.

## Synchronization
If either AI says a milestone is complete but QA/runtime gates are incomplete:
```text
MILESTONE = OPEN
```

## Runtime Gate
Every milestone must prove backend, frontend, database, ports, changed APIs, changed UI where applicable, regressions, logs and Git state.

## Scope Control
Classify discovered issues as:
- blocking current milestone
- non-blocking defect
- deferred feature
- future hardening
- architectural concern

Do not silently expand scope.

## Global Mobility Rule
Visa/migration/global mobility is later-stage functionality and must not hijack the core job-hunting roadmap.

## Next Milestone
Only after:
```text
FAIL = 0
PENDING = 0
QA = PASS
RUNTIME = PASS
STABILITY = PASS
```
may ChatGPT issue the next milestone brief.

## Closeout Marker
```text
[CAREEROS: MILESTONE <name> — VERIFIED]
Commit: <sha>
Runtime: PASS
QA: PASS
Stability: PASS
Next milestone: <name>
Authorization: ISSUED
```
