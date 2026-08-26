# CareerOS — AI-to-AI Coordination & Milestone Orchestration Protocol

**Protocol ID:** CAREEROS-AI-COLL-001  
**Applies to:** v0.2 Global Job Intelligence and all future versions  
**Repository:** `arunramakantsingh-coder/CareerOS`  
**Active development branch:** `release/v0.2-global-job-intelligence`

---

## 1. Purpose

This protocol defines how CareerOS is developed using two AI roles with the human project owner acting as the controlled integration bridge.

The objective is to prevent:

- role confusion
- duplicated coding
- undocumented architecture changes
- "works on my machine" claims
- unverified milestone completion
- UI/backend divergence
- lost context between ChatGPT and DeepSeek
- undocumented code transferred between AI systems

The protocol creates a repeatable loop:

```text
CHATGPT
Lead Architect / QA / Reviewer
        |
        | Approved Milestone / Implementation Brief
        v
HUMAN PROJECT OWNER
        |
        | Exact instruction + context
        v
DEEPSEEK
Developer / Coder
        |
        | Code + tests + milestone evidence
        v
HUMAN PROJECT OWNER
        |
        | Applies code in VS Code
        | Runs local validation
        | Captures evidence
        v
GITHUB / WORKING BRANCH
        |
        | Repository inspection
        v
CHATGPT
Architecture + QA + Security Review
        |
        +--> FIX REQUIRED
        |
        +--> APPROVED FOR NEXT VALIDATION
        |
        +--> VERIFIED
```

---

# 2. Roles

## 2.1 ChatGPT — Lead Architect / QA / Reviewer

ChatGPT is responsible for:

- product architecture
- architecture governance
- requirement interpretation
- milestone definition
- acceptance criteria
- security review
- code/repository review
- API/database/frontend contract review
- regression review
- QA planning
- test-result interpretation
- defect classification
- release readiness
- final `VERIFIED` / `NOT VERIFIED` decision

ChatGPT is the **verification authority**.

ChatGPT must not assume that an implementation is correct merely because DeepSeek reports success.

---

## 2.2 DeepSeek — Developer / Coder

DeepSeek is responsible for:

- repository inspection for the requested task
- implementation
- refactoring
- bug fixes
- database changes
- Alembic migrations
- API implementation
- frontend implementation
- test implementation
- PowerShell automation
- local technical diagnostics
- implementation evidence
- milestone completion report

DeepSeek is the **implementation authority**, not the final verification authority.

DeepSeek must never silently change the approved architecture or milestone scope.

---

## 2.3 Human Project Owner — Arun

The human project owner is the controlled bridge between the two AIs.

Responsibilities:

1. Copy ChatGPT's approved implementation brief to DeepSeek.
2. Receive DeepSeek's complete implementation package.
3. Apply the approved code/scripts in VS Code.
4. Run the requested local commands/tests.
5. Capture actual runtime evidence.
6. Commit/push the reviewed state to the correct Git branch when instructed.
7. Provide DeepSeek evidence and/or GitHub state back to ChatGPT.
8. Never manually modify generated code between AI handoffs without reporting the modification.

The human is the **execution and evidence bridge**, not the architecture authority.

---

# 3. Source-of-Truth Hierarchy

Use the following order:

```text
1. Approved Git repository implementation
2. Current CareerOS control-plane documentation
3. Approved ChatGPT milestone instruction
4. DeepSeek implementation report
5. Local runtime evidence
6. Historical ZIPs / temporary folders
```

However, each source proves a different thing.

### Repository proves

- what code is actually present
- what files exist
- what was committed
- what changed

### DeepSeek report proves

- what DeepSeek intended to implement
- what files it believes it changed
- what commands it says it executed
- what technical tests it reports

### Local runtime evidence proves

- whether the application actually ran in the user's environment
- whether the specific user environment exposes defects
- whether UI/API/database behavior actually works

### ChatGPT review proves

- architectural conformity
- requirement conformity
- QA acceptance
- security review
- whether available evidence is sufficient for `VERIFIED`

No single source is sufficient for all four dimensions.

---

# 4. The Three-Evidence Verification Model

CareerOS uses three independent evidence sources.

## Evidence A — Implementation Evidence

Produced by DeepSeek.

Must include:

- files created
- files modified
- database changes
- migrations
- API changes
- UI changes
- tests executed
- commands executed
- build result
- known issues
- blockers
- implementation status

---

## Evidence B — Local Runtime Evidence

Produced by the human project owner after applying DeepSeek's changes.

Must include, where applicable:

- Docker/Compose result
- backend startup
- database/migration result
- backend tests
- frontend build
- API smoke tests
- browser/UI results
- screenshots
- browser console errors
- critical user-flow results

The human must not report a test as passed simply because the command was launched.

---

## Evidence C — Repository Evidence

Produced by ChatGPT through GitHub/repository inspection where available.

ChatGPT should independently inspect:

- branch
- commit
- changed files
- diff
- migration files
- API changes
- frontend changes
- tests
- documentation changes
- unexpected files
- accidental generated artifacts
- architecture drift

If GitHub access is unavailable, ChatGPT must say:

`REPOSITORY REVIEW NOT EXECUTED — GITHUB ACCESS UNAVAILABLE`

and cannot claim repository-level verification.

---

# 5. The Milestone Lifecycle

Every milestone follows the same state machine:

```text
PLANNED
   |
   v
ARCHITECTURALLY APPROVED
   |
   v
IMPLEMENTING
   |
   v
IMPLEMENTED
   |
   v
LOCAL TESTED
   |
   v
REPOSITORY REVIEW
   |
   v
QA REVIEW
   |
   +------> FIX REQUIRED
   |            |
   |            v
   |        IMPLEMENTING
   |
   v
VERIFIED
```

Alternate terminal state:

```text
BLOCKED
```

---

# 6. Gate 1 — ChatGPT Creates the Milestone Brief

Before DeepSeek writes code, ChatGPT must define:

```text
MILESTONE ID
MILESTONE NAME
OBJECTIVE
BUSINESS PURPOSE
ARCHITECTURE SCOPE
FILES / MODULES EXPECTED
DATABASE IMPACT
API IMPACT
UI IMPACT
TEST REQUIREMENTS
SECURITY REQUIREMENTS
NON-GOALS
ACCEPTANCE CRITERIA
STOP CONDITION
```

The implementation brief must be small enough for one controlled development cycle.

ChatGPT must not ask DeepSeek to implement the entire product in one instruction.

---

# 6A. SINGLE ACTIVE MILESTONE — HARD SYNCHRONIZATION RULE

CareerOS must have exactly ONE `ACTIVE MILESTONE` at any time.

The milestone state is controlled by a shared coordination record:

```text
ACTIVE_MILESTONE
MILESTONE_STATE
IMPLEMENTATION_OWNER
QA_OWNER
HUMAN_ACTION
LAST_VERIFIED_COMMIT
```

The following rule is mandatory:

> DeepSeek MUST NOT start the next milestone while the current milestone is not `VERIFIED` by ChatGPT.

A DeepSeek response that proposes or begins a later milestone while the current milestone is:

- `IMPLEMENTING`
- `IMPLEMENTED`
- `LOCAL TESTED`
- `FIX REQUIRED`
- `NOT VERIFIED`
- `BLOCKED`

must be treated as **out of sequence**.

ChatGPT must explicitly stop that progression and return the project to the current active milestone.

---

# 6B. MILESTONE SYNCHRONIZATION HANDSHAKE

Every AI-to-AI handoff must carry these fields:

```text
ACTIVE MILESTONE:
MILESTONE STATE:
LAST APPROVED TASK:
LAST IMPLEMENTATION COMMIT:
LAST LOCAL TEST RESULT:
NEXT ALLOWED ACTION:
```

Example:

```text
ACTIVE MILESTONE:
M6 — Semantic Matching Engine

MILESTONE STATE:
QA REVIEW

LAST APPROVED TASK:
Implement capability/evidence matching and hard-failure separation.

LAST IMPLEMENTATION COMMIT:
abc1234

LAST LOCAL TEST RESULT:
PASS — matching unit/API tests

NEXT ALLOWED ACTION:
ChatGPT QA review only.

DO NOT START:
M7 / Resume Studio
```

---

# 6C. QUALITY CHECK IS A GATE, NOT A DELAY

When ChatGPT is in `QA REVIEW`, DeepSeek must remain on the same milestone.

DeepSeek may only:

- answer QA questions
- provide missing evidence
- fix findings explicitly returned by ChatGPT
- rerun requested tests
- provide updated implementation evidence

DeepSeek may NOT:

- start the next milestone
- refactor unrelated modules
- add future features
- change the roadmap
- declare the current milestone verified

---

# 6D. OUT-OF-SEQUENCE DETECTION

If ChatGPT discovers that DeepSeek has started a later milestone before QA verification, ChatGPT must issue:

```text
[CAREEROS SYNCHRONIZATION STOP]

CURRENT ACTIVE MILESTONE:
<current>

CURRENT STATE:
<state>

DEEPSEEK HAS ADVANCED TO:
<later milestone>

ACTION:
STOP IMPLEMENTATION OF THE LATER MILESTONE.

RETURN TO:
<current milestone>

REQUIRED:
1. Reconcile current milestone status.
2. Submit implementation evidence.
3. Resolve QA findings.
4. Execute required tests.
5. Wait for VERIFIED.

NO NEXT MILESTONE AUTHORIZATION.
```

The human should forward this message verbatim to DeepSeek.

---

# 6E. MILESTONE AUTHORIZATION TOKEN

To make copy/paste coordination unambiguous, ChatGPT should end every milestone decision with exactly one status token:

```text
[CAREEROS: MILESTONE <ID> — FIX REQUIRED]
[CAREEROS: MILESTONE <ID> — QA REVIEW]
[CAREEROS: MILESTONE <ID> — APPROVED FOR LOCAL VALIDATION]
[CAREEROS: MILESTONE <ID> — VERIFIED]
[CAREEROS: MILESTONE <ID> — BLOCKED]
```

DeepSeek may act only on the currently authorized status.

### Meaning

`FIX REQUIRED`
→ DeepSeek may modify only the current milestone.

`QA REVIEW`
→ DeepSeek must wait or provide requested evidence/fixes.

`APPROVED FOR LOCAL VALIDATION`
→ Human runs the approved implementation and returns runtime evidence.

`VERIFIED`
→ Current milestone is closed; next milestone may be opened.

`BLOCKED`
→ No implementation progression until blocker is resolved.

---

# 6G. MILESTONE CLOSEOUT RECORD

At the end of every verified milestone, ChatGPT must publish a closeout record:

```text
MILESTONE CLOSEOUT

MILESTONE:
STATUS: VERIFIED

IMPLEMENTATION COMMIT:
<hash>

LOCAL VALIDATION:
<PASS/FAIL>

REPOSITORY REVIEW:
<PASS/FAIL>

QA REVIEW:
<PASS/FAIL>

KNOWN OPEN ISSUES:
<none or list>

NEXT AUTHORIZED MILESTONE:
<id/name>
```

Only this closeout record authorizes DeepSeek to move forward.

# 7. Gate 2 — DeepSeek Performs Repository Inspection

DeepSeek must inspect the current repository before changing code.

At minimum inspect:

- current branch
- git status
- relevant documentation
- relevant backend modules
- frontend modules
- DB models
- Alembic migrations
- existing tests
- related API routes
- related UI routes/components
- existing duplicate implementations
- current TODO/stub state

DeepSeek should state what it found before implementation.

---

# 8. Gate 3 — DeepSeek Implements

DeepSeek implements only the approved milestone.

Preferred sequence:

```text
EXTEND
  ->
REFACTOR
  ->
FIX
```

Use:

```text
DELETE
  ->
REBUILD
```

only when the existing implementation is fundamentally incompatible and the reason is explicitly reported.

DeepSeek must not:

- create parallel modules unnecessarily
- change unrelated architecture
- change product version boundaries
- introduce hidden dependencies
- silently modify security boundaries
- silently replace the database architecture
- add fake UI behavior as proof of backend completion

---

# 9. DeepSeek Implementation Package

At the end of every milestone, DeepSeek MUST provide a structured summary.

Required format:

```text
[DEEPSEEK — DEVELOPER / CODER]

MILESTONE:
<id and name>

OBJECTIVE:
<what was implemented>

IMPLEMENTATION SUMMARY:
<short technical summary>

FILES CREATED:
<list>

FILES MODIFIED:
<list>

FILES DELETED:
<list, if any>

ARCHITECTURE CHANGES:
<none or details>

DATABASE CHANGES:
<models/schema changes>

MIGRATIONS:
<migrations created/modified>

BACKEND/API:
<routes/services/schemas>

FRONTEND/UI:
<pages/components/hooks/client changes>

AI/DOMAIN LOGIC:
<agents/services/logic>

TESTS EXECUTED:
<exact command>
<result>

BUILD EXECUTED:
<exact command>
<result>

SECURITY CHECKS:
<exact command/result or NOT EXECUTED>

LOCAL LIMITATIONS:
<limitations>

KNOWN BUGS:
<bugs>

BLOCKERS:
<blockers>

IMPLEMENTATION STATUS:
IMPLEMENTED / PARTIAL / BLOCKED

RECOMMENDATION:
<what ChatGPT should review next>
```

DeepSeek must never use `VERIFIED` as its own milestone status.

---

# 10. Human Integration Gate

After receiving DeepSeek's implementation package, the human project owner applies the code in VS Code.

The human must:

1. run the DeepSeek-provided PowerShell implementation script(s)
2. inspect the changed files
3. run the provided test/validation script(s)
4. launch the required services
5. perform requested UI validation
6. capture actual errors/results
7. preserve the output

If the implementation requires a manual code copy, DeepSeek must provide complete file content and explicit file paths.

Preferred approach:

```text
DeepSeek
   ->
Complete PowerShell implementation script
   ->
VS Code terminal
   ->
Files created/modified
```

---

# 11. Human Local Evidence Package

For every milestone, the human should provide ChatGPT:

```text
[LOCAL RUNTIME EVIDENCE]

MILESTONE:
<id>

BRANCH:
<current branch>

COMMIT:
<commit if already committed>

ENVIRONMENT:
<Windows / Docker / etc.>

BUILD RESULT:
<result>

BACKEND TEST RESULT:
<result>

DATABASE/MIGRATION RESULT:
<result>

API RESULT:
<result>

UI RESULT:
<result>

E2E RESULT:
<result>

SCREENSHOTS:
<list if applicable>

LOGS:
<paths or relevant excerpts>

ERRORS:
<exact errors>

HUMAN OBSERVATION:
<what was actually seen>
```

---

# 12. GitHub Cross-Check Rule

YES — ChatGPT should cross-check DeepSeek's work in GitHub whenever ChatGPT has repository access.

This is strongly recommended.

But GitHub review does NOT replace local runtime testing.

The two checks answer different questions.

### GitHub check

> "Did the intended code actually make it into the repository?"

### Local runtime check

> "Does that code actually work in the user's real environment?"

### ChatGPT QA

> "Does the implementation satisfy the product/architecture/security/acceptance contract?"

All three are required for a normal `VERIFIED` milestone.

---

# 13. Repository Review Procedure for ChatGPT

After the human pushes the milestone state, ChatGPT should inspect:

## A. Branch

Confirm the expected branch.

## B. Commit

Confirm the expected commit exists.

## C. Diff

Review changed files.

## D. Unexpected files

Look for:

- secrets
- generated files
- node_modules
- .next
- caches
- test-result dumps
- temporary scripts
- duplicate implementations
- unrelated edits

## E. Database

Inspect:

- models
- migration
- migration ordering
- consistency

## F. Backend

Inspect:

- API
- services
- schemas
- authorization
- tenant isolation

## G. Frontend

Inspect:

- routes
- components
- API integration
- loading/empty/error states

## H. Tests

Inspect:

- tests added/updated
- boundary tests
- security tests
- expected integration tests

---

# 14. Important: GitHub Review Timing

The preferred sequence is:

```text
DeepSeek implements
      ↓
Human applies in VS Code
      ↓
Human runs local tests
      ↓
Human confirms results
      ↓
Human commits/pushes milestone candidate
      ↓
ChatGPT reviews GitHub
      ↓
ChatGPT requests fixes OR approves
```

Do not push half-implemented experimental work to the release branch just to allow review.

Use the appropriate feature/work branch where necessary.

---

# 15. Recommended Git Branch Model

For v0.2:

```text
release/v0.2-global-job-intelligence
        |
        +-- feature/<milestone>
        |
        +-- feature/<milestone>
        |
        +-- fix/<bug>
```

Preferred flow:

```text
feature branch
    ↓
local validation
    ↓
ChatGPT review
    ↓
merge / controlled promotion
    ↓
release/v0.2-global-job-intelligence
```

The release branch should represent an accepted integration state.

---

# 16. QA Decision Format

ChatGPT's response after reviewing DeepSeek should use:

```text
[CHATGPT — LEAD ARCHITECT / QA / REVIEWER]

MILESTONE:
<id/name>

ARCHITECTURE RESULT:
PASS / FAIL

CODE REVIEW:
PASS / FAIL

DATABASE REVIEW:
PASS / FAIL / N/A

API REVIEW:
PASS / FAIL / N/A

UI REVIEW:
PASS / FAIL / N/A

SECURITY REVIEW:
PASS / FAIL / N/A

TEST EVIDENCE:
PASS / FAIL / INSUFFICIENT

REPOSITORY REVIEW:
PASS / FAIL / NOT EXECUTED

LOCAL RUNTIME EVIDENCE:
PASS / FAIL / INSUFFICIENT

REGRESSION RISK:
LOW / MEDIUM / HIGH

DECISION:
VERIFIED
or
FIX REQUIRED
or
BLOCKED
or
NOT VERIFIED

REQUIRED ACTIONS:
<exact actions>
```

---

# 17. What "VERIFIED" Means

A milestone may be marked `VERIFIED` only when:

- approved requirements are implemented
- architecture conforms
- DB changes are correct
- migrations are correct
- APIs work
- UI works where applicable
- API/UI integration works
- relevant tests pass
- security checks pass where applicable
- tenant isolation passes where applicable
- local runtime evidence exists
- repository review exists where GitHub access is available
- no known critical defect remains
- documentation/status is updated

`VERIFIED` is a QA/release state, not a coding state.

---

# 18. Skill Gap Intelligence — Mandatory Verification Rules

When matching functionality is implemented, QA must verify all of the following:

```text
Skill Match < 60%
    ->
not highlighted as the 60% opportunity threshold

Skill Match = 60%
    ->
highlighted

Skill Match > 60%
    ->
highlighted
```

The system must clearly distinguish:

- matched
- partial
- transferable
- missing
- mandatory missing
- hard failure

It must also persist:

```text
SkillGapObservation
```

and support cumulative:

```text
SkillGapAggregate
```

The cumulative record must be usable to identify:

- frequent gaps
- mandatory gaps
- persona-specific gaps
- role-family gaps
- recurring technology gaps
- learning priorities
- profile-improvement opportunities

A UI badge alone is insufficient.

---

# 19. UI/Backend Gate

For any functional module:

```text
DB
 ->
Backend
 ->
API
 ->
Frontend
 ->
Integration
 ->
Tests
 ->
E2E
 ->
QA
 ->
VERIFIED
```

If the backend is implemented but the UI is not connected:

`NOT VERIFIED`

If the UI exists using fake data:

`NOT VERIFIED`

If the UI route works but the API contract is broken:

`NOT VERIFIED`

---

# 20. Failure Escalation

## P0

- security breach
- tenant data leakage
- destructive data corruption
- credential exposure

Immediate stop.

## P1

- core user journey broken
- major data integrity problem
- authentication/authorization failure

Stop milestone promotion.

## P2

- major feature defect
- recoverable workflow failure

Fix before milestone verification.

## P3

- minor bug
- UX defect

May remain open only if explicitly accepted.

## P4

- cosmetic issue
- low-priority enhancement

Track separately.

---

# 21. Communication Rule Between the AIs

The AIs do not assume direct communication.

The human is the explicit bridge.

When a message is copied from one AI to the other, preserve:

- sender role
- receiver role
- milestone
- instruction/report
- evidence
- known limitations
- requested action

Neither AI should assume facts that were not included in the handoff.

---

# 22. ChatGPT Must Not Ask "Did You Actually Run It?" If Evidence Exists

If DeepSeek provides exact executed commands and the human provides actual runtime output, use those as evidence.

If evidence is missing, say exactly what is missing.

Avoid unnecessary repeated testing.

The objective is reliable verification, not repetitive ceremony.

---

# 23. DeepSeek Must Not Ask ChatGPT to "Trust the Code"

DeepSeek should provide evidence.

Preferred:

```text
pytest command
result
migration command
result
build command
result
API smoke command
result
```

Not:

```text
The feature should work.
```

---

# 24. Human Must Not Manually Patch Between Review Cycles Without Disclosure

If the human changes code after DeepSeek's response:

```text
MANUAL CHANGE DETECTED
```

must be reported to ChatGPT.

The changed files must be identified.

Otherwise ChatGPT may review code that differs from DeepSeek's implementation report.

---

# 25. Milestone Summary Is Mandatory

At the END of EVERY milestone, DeepSeek must produce a concise human-readable summary:

```text
MILESTONE COMPLETE — IMPLEMENTATION SUMMARY

What was built:
What changed:
What is now possible:
What was tested:
What was not tested:
Known limitations:
Files changed:
Recommended QA focus:
```

This summary is separate from the detailed technical report.

---

# 26. ChatGPT QA Focus Is Mandatory

At the END of EVERY milestone, ChatGPT must produce:

```text
QA SUMMARY

What was verified:
What was not verified:
Critical findings:
Required fixes:
Regression risks:
Next milestone recommendation:
```

---

# 27. No Automatic Promotion

Neither AI may decide:

> "Let's continue to the next module"

unless the current milestone has passed its required gate.

The next milestone starts only after the current milestone is:

`VERIFIED`

or explicitly marked as an accepted partial milestone.

---

# 28. Final Coordination Principle

CareerOS development is not:

```text
AI writes code -> AI says done
```

It is:

```text
Architect
  ↓
Developer
  ↓
Human execution
  ↓
Runtime evidence
  ↓
Repository evidence
  ↓
QA
  ↓
Fix
  ↓
Re-test
  ↓
VERIFY
```

This protocol is mandatory for CareerOS milestone development.

---

# 29. Synchronization Principle

There is never more than one active milestone.

The project must remain synchronized as:

```text
CHATGPT ACTIVE MILESTONE
        =
DEEPSEEK ACTIVE MILESTONE
        =
HUMAN EXECUTION MILESTONE
        =
GITHUB RELEASE CANDIDATE MILESTONE
```

If those four diverge, stop development and reconcile the state before continuing.

---

# 30. ABSOLUTE EVIDENCE RULE — NO PREDECLARED TEST RESULTS

DeepSeek MUST NOT describe a test as PASS, VERIFIED, COMPLETE or SUCCESSFUL
until the test has actually been executed in the current environment.

These are different states:

PLANNED
TEST SCRIPT WRITTEN
TEST READY
TEST EXECUTED
TEST PASSED
TEST FAILED
NOT EXECUTED

The following are NOT evidence:

- a test script that has been written
- an expected output
- a predicted result
- a simulated result
- a manually printed "PASS"
- a commit message claiming a result
- an implementation summary claiming a result
- an assertion that the code "should work"

A test is "PASSED" only when:

1. the command actually executed;
2. the output was captured;
3. the output supports the stated result.

## Commit-message rule

DeepSeek MUST NOT create a commit message that states:

- test passed
- gate complete
- health check passed
- migration fixed
- QA complete
- verified

unless those results have actually been executed and evidenced.

Commit messages describe IMPLEMENTED changes.

QA status belongs to ChatGPT after evidence review.

## Evidence separation

Every milestone report must separate:

### IMPLEMENTATION STATUS

What code was written.

### TEST PLAN

What commands should be run.

### ACTUAL TEST EXECUTION

Commands that were actually executed.

### ACTUAL TEST OUTPUT

The real captured output.

### QA STATUS

ChatGPT's independent assessment.

Example:

TEST PLAN:
`curl.exe http://localhost:8000/api/v1/health`

ACTUAL EXECUTION:
NOT YET EXECUTED

ACTUAL RESULT:
NOT AVAILABLE

QA STATUS:
NOT VERIFIED

# 30. ABSOLUTE EVIDENCE RULE — NO PREDECLARED TEST RESULTS

DeepSeek MUST NOT describe a test as PASS, VERIFIED, COMPLETE or SUCCESSFUL
until the test has actually been executed in the current environment.

These are different states:

PLANNED
TEST SCRIPT WRITTEN
TEST READY
TEST EXECUTED
TEST PASSED
TEST FAILED
NOT EXECUTED

The following are NOT evidence:

- a test script that has been written
- an expected output
- a predicted result
- a simulated result
- a manually printed "PASS"
- a commit message claiming a result
- an implementation summary claiming a result
- an assertion that the code "should work"

A test is "PASSED" only when:

1. the command actually executed;
2. the output was captured;
3. the output supports the stated result.

## Commit-message rule

DeepSeek MUST NOT create a commit message that states:

- test passed
- gate complete
- health check passed
- migration fixed
- QA complete
- verified

unless those results have actually been executed and evidenced.

Commit messages describe IMPLEMENTED changes.

QA status belongs to ChatGPT after evidence review.

## Evidence separation

Every milestone report must separate:

### IMPLEMENTATION STATUS

What code was written.

### TEST PLAN

What commands should be run.

### ACTUAL TEST EXECUTION

Commands that were actually executed.

### ACTUAL TEST OUTPUT

The real captured output.

### QA STATUS

ChatGPT's independent assessment.

Example:

TEST PLAN:
`curl.exe http://localhost:8000/api/v1/health`

ACTUAL EXECUTION:
NOT YET EXECUTED

ACTUAL RESULT:
NOT AVAILABLE

QA STATUS:
NOT VERIFIED
