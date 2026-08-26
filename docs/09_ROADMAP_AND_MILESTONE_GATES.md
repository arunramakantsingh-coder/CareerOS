# CareerOS — Roadmap & Milestone Gates

## Operating method

Use:

```text
AGENTS.md
+
relevant specification
+
one current task
```

Then:

```text
Inspect
→ Understand
→ Plan
→ Implement
→ Test
→ Review
→ Fix
→ Document
→ Verify
```

One task/phase at a time.

---

# Phase 0 — Repository Reconciliation

Inspect:

- repository
- docs
- current code
- old assessment
- MASTER/FIXED differences
- duplicate code
- migrations
- tests
- Docker
- Lovable reference

No modifications during the initial audit.

---

# Phase 1 — Foundation Repair

Verify:

- dependencies
- Docker
- PostgreSQL
- pgvector
- Alembic
- backend build
- frontend build
- health endpoints

---

# Phase 2 — Database Integrity

Verify:

- model/migration consistency
- relationships
- indexes
- ownership
- evidence
- vector fields
- clean DB
- existing DB

---

# Phase 3 — Authentication & Tenant Security

Implement/verify:

- registration
- login
- hashing
- JWT
- current user
- tenant context
- RBAC
- protected APIs

---

# Phase 4 — Security Hardening

- exceptions
- request IDs
- logging
- rate limits
- validation
- secure uploads
- SSRF defenses
- prompt-injection defenses

---

# Phase 5 — Testing Foundation

- pytest
- pytest-asyncio
- DB tests
- API tests
- auth tests
- tenant tests
- frontend build checks
- CI where practical

---

# Phase 6 — Career Vault

- CV import
- career CRUD
- evidence
- provenance
- unified record
- UI

---

# Phase 7 — Personas

- default personas
- custom
- activation
- cloning
- weights
- target roles/locations/industries
- salary/work mode

---

# Phase 8 — Job Intelligence

- manual JD
- normalization
- deduplication
- extraction
- Job DNA
- mandatory/preferred

---

# Phase 9 — Career Ontology + Matching

- capability ontology
- embeddings
- retrieval
- scoring
- hard failures
- explanation
- persona recommendation

---

# Phase 10 — pgvector

- extension
- embedding provider abstraction
- fields/indexes
- retrieval
- caching
- versioning
- cost

---

# Phase 11 — Resume + Truth

- JD-to-evidence
- tailored resume
- ATS
- truth validation
- immutable versions

---

# Phase 12 — Application Factory

- cover letter
- answers
- recruiter message
- hiring-manager message
- approval

---

# Phase 13 — Application CRM

- state machine
- recruiter
- interviews
- offers
- notes
- reminders
- versions
- history

---

# Phase 14 — Remote Intelligence

- worldwide vs restricted
- timezone
- work authorization
- employment model
- relocation
- sponsorship

---

# Phase 15 — Company + Interview Intelligence

- permitted company research
- role context
- interview preparation
- round tracking
- outcomes

---

# Phase 16 — Global Mobility

Australia first, New Zealand next, then:

- UAE
- Qatar
- Saudi Arabia
- Singapore
- UK
- Canada
- Germany/EU

Use versioned official rules.

---

# Phase 17 — Frontend

Build/verify:

- dashboard
- Career Vault
- personas
- jobs
- applications
- mobility
- interviews
- analytics
- settings
- shared shell

Connect all to real APIs.

---

# Phase 18 — Job Connectors

Start with:

- manual
- permitted employer pages
- generic API/feed framework

Add portals according to terms/access conditions.

---

# Phase 19 — Analytics

Track:

- discovery
- shortlist
- applications
- interviews
- offers
- acceptance/rejection
- persona/source/country/salary/capability

---

# Phase 20 — AI Orchestration & Cost

- provider abstraction
- embeddings
- caching
- routing
- cost tracking
- selective evidence retrieval

---

# Phase 21 — Production Hardening

- logging
- metrics
- backups
- Docker
- Nginx
- environments
- performance
- CI/CD

---

# Phase 22 — SaaS Entitlements

- Free
- Pro
- Global
- Executive
- server-side usage enforcement

Payment can wait.

---

# Phase 23 — End-to-End Acceptance

```text
User
→ Career Vault
→ Persona
→ JD
→ Job DNA
→ Match
→ 60% Skill Highlight
→ Skill Gaps
→ Hard Failures
→ Resume
→ Truth
→ Application
→ Approval
→ CRM
→ Remote
→ Mobility
→ Outcome
```

Plus:

- tenant isolation
- migrations
- backend tests
- frontend build
- security tests

---

# Milestone gate

A milestone is `VERIFIED` only when:

- implementation exists
- tests actually executed
- relevant build passes
- integration works
- no critical regression
- documentation is updated
- reviewer accepts evidence

Otherwise:

`NOT VERIFIED`.
