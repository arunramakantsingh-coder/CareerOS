# CareerOS — AI-to-AI Work Protocol

## 1. Shared operating model

```text
Product Owner / Human
        │
        ▼
ChatGPT
Lead Architect / QA / Reviewer
        │
        ▼
Approved Task
        │
        ▼
DeepSeek
Developer / Coder
        │
        ▼
Implementation + Tests
        │
        ▼
ChatGPT Review
        │
   ┌────┴─────┐
   ▼          ▼
Verified   Fix Required
```

---

# 2. ChatGPT → DeepSeek task format

```text
MILESTONE:
TASK:

OBJECTIVE:

AUTHORITATIVE DOCUMENTS:

CURRENT STATE:

REQUIRED BEHAVIOR:

DATABASE:

API:

UI:

TESTS:

SECURITY:

NON-GOALS:

ACCEPTANCE CRITERIA:

STOP CONDITION:
```

---

# 3. DeepSeek → ChatGPT response

```text
IMPLEMENTATION REPORT

MILESTONE:
TASK:

FILES CREATED:
FILES MODIFIED:

ARCHITECTURE:

DATABASE:
MIGRATIONS:

BACKEND:
API:

FRONTEND:
UI:

TESTS EXECUTED:

BUILD:

SECURITY:

E2E:

KNOWN LIMITATIONS:

BLOCKERS:

STATUS:
IMPLEMENTED / TESTED / BLOCKED
```

---

# 4. ChatGPT review result

Use:

- APPROVED FOR QA
- FIX REQUIRED
- BLOCKED
- VERIFIED

---

# 5. Bug report format

```text
BUG ID:
SEVERITY:
MODULE:
ENVIRONMENT:

EXPECTED:
ACTUAL:

REPRODUCTION:

EVIDENCE:

ROOT CAUSE:

FIX:

REGRESSION RISK:

RETEST:
```

---

# 6. Architecture Decision Record

For material decisions:

```text
ADR:
DATE:
CONTEXT:
DECISION:
OPTIONS:
CHOSEN:
WHY:
IMPACT:
REJECTED OPTIONS:
APPROVAL:
```

---

# 7. Stop rules for DeepSeek

Stop and ask ChatGPT/owner review if:

- data model changes materially
- security changes materially
- version boundary changes
- external integration changes
- privacy changes
- automation policy changes
- incompatible architecture discovered
- docs conflict cannot be resolved

---

# 8. Evidence package

A milestone evidence package should contain:

- branch
- commit
- changed files
- migration output
- backend tests
- frontend build
- API smoke
- security
- E2E
- screenshots where useful
- logs
- known issues

---

# 9. Verification

The final state is:

`VERIFIED`

only after actual evidence and reviewer approval.
