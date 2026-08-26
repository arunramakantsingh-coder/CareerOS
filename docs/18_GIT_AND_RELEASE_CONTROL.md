# CareerOS — Git, Branching & Release Control

## Repository

`arunramakantsingh-coder/CareerOS`

## Canonical release strategy

```text
main
│
├── release/v0.1-personal-job-interview-copilot
│       └── v0.1.0
│
└── release/v0.2-global-job-intelligence
```

---

# v0.1 baseline

Conversation-confirmed:

```text
Commit:
8ced9f9

Message:
release: CareerOS v0.1 Personal Job & Interview Copilot
```

Release tag:

```text
v0.1.0
```

This is the frozen v0.1 baseline.

---

# v0.2 branch

Conversation-confirmed:

```text
release/v0.2-global-job-intelligence
```

It was created from the v0.1.0 baseline.

Therefore the branch starts with the same v0.1 foundation.

---

# Branch rules

### v0.1 release branch

Do not add unplanned v0.2 functionality.

Bug/security fixes only when necessary and controlled.

### v0.2 branch

Active development line for Global Job Intelligence.

### main

Protected release/integration branch according to repository workflow.

Do not make silent direct changes.

---

# Commit rules

Use focused commits.

Examples:

```text
feat(skill-gap): add cumulative skill-gap domain
feat(match): expose 60 percent skill highlight
feat(jobs): add capability discovery
feat(ui): connect match card to real API
test(skill-gap): add aggregation tests
fix(auth): enforce tenant ownership
docs(handoff): update v0.2 architecture
```

---

# Release tag rules

A tag is created only after the corresponding release branch reaches release acceptance.

Do not tag a merely "looks good" state.

---

# ZIP delivery rule

The repository synchronization document defines:

- Git repository = canonical commits/history
- test ZIP = clean non-Git local-validation delivery copy
- no `.git`
- no generated builds
- no dependency folders
- no DB volumes
- no secrets

The human can validate the ZIP locally before release push.

---

# Human approval

Require owner approval for:

- release tagging
- release pushing
- destructive history changes
- material architecture changes
- external automation
- privacy/security changes
