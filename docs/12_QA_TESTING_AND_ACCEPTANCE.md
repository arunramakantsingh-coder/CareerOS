# CareerOS — QA, Testing & Acceptance Framework

## QA principle

A script is an execution tool, not proof.

A source file is not proof.

A 200 response is not proof of end-to-end correctness.

Verification requires actual evidence.

---

# 1. Test layers

```text
Static / code review
↓
Unit
↓
Database / migration
↓
API
↓
Security
↓
Frontend build/UI
↓
Integration
↓
E2E
↓
Release acceptance
```

---

# 2. Foundation tests

- Python syntax
- imports
- backend startup
- database connection
- migration
- frontend TypeScript
- Next.js build
- Compose validation
- health endpoints

---

# 3. Authentication

- registration
- duplicate registration
- login
- wrong password
- token
- current user
- invalid/expired token
- password reset
- OAuth architecture
- phone verification
- WhatsApp verification when integrated

---

# 4. Tenant isolation

```text
User A / Tenant A → Tenant A = ALLOW
User A / Tenant A → Tenant B = DENY
User B / Tenant B → Tenant B = ALLOW
```

Test every user-owned domain.

---

# 5. Career Vault

- multi-CV upload
- parsing
- duplicate handling
- conflict handling
- provenance
- editing
- persistence
- authorization

---

# 6. Personas

- default personas
- custom
- create
- update
- activate
- clone
- weights
- target roles
- location
- country
- salary
- work mode

---

# 7. Job/JD

- manual import
- permitted source
- normalization
- dedupe
- source retention
- canonical JD
- mandatory/preferred
- role family
- seniority
- responsibility
- skills
- technologies

---

# 8. Job DNA

Verify:

- role family
- seniority
- capabilities
- technologies
- responsibilities
- architecture
- leadership
- governance
- industry
- location
- employment
- salary
- constraints

---

# 9. Matching

Test:

- direct match
- synonym
- transferable
- partial
- missing
- hard failure
- persona recommendation
- scoring weights
- explanation

---

# 10. 60% Skill-Match

Required boundary tests:

```text
59% → not highlighted
60% → highlighted
61% → highlighted
```

Also:

- Skill Match 80 + hard failure → highlight skill match, show hard failure
- Skill Match 55 + Career Fit 90 → no 60% skill highlight
- Skill Match 65 + Career Fit 55 → highlight skill match, but do not call it a high overall career fit
- missing skills visible
- mandatory missing visible
- transferable skills visible

---

# 11. Skill Gap Intelligence

Test:

- observations persist
- repeated skills aggregate
- duplicate job processing does not inflate counts
- mandatory missing count
- persona impact
- role-family impact
- priority
- learning status
- recomputation
- tenant isolation

---

# 12. Resume / Truth

- JD-to-evidence
- ATS
- supported claims
- unsupported claims
- partial support
- Truth gate
- immutable version

---

# 13. Application Factory

- resume package
- cover letter
- application answers
- recruiter message
- hiring-manager message
- approval
- versioning

---

# 14. CRM

Test state machine:

```text
DISCOVERED
ANALYZED
SHORTLISTED
READY_FOR_REVIEW
APPROVED
APPLIED
RECRUITER_CONTACT
INTERVIEW
OFFER
ACCEPTED
```

and:

- REJECTED
- WITHDRAWN
- ON_HOLD

Invalid transitions rejected.

---

# 15. Company Intelligence

Verify:

- source
- confidence
- timestamp
- no fabricated data
- association with job
- recruiter/hiring context

---

# 16. Interview

- technical
- architecture
- behavioral
- company
- role
- question prediction
- preparation
- mock
- round tracking
- notes
- outcomes

---

# 17. Live Interview

- context
- input/transcription
- question detection
- retrieval
- evidence
- response guidance
- user control

---

# 18. Remote

Test:

- worldwide
- restricted
- timezone
- authorization
- employment model
- contractor/EOR
- relocation
- sponsorship

---

# 19. Global Mobility

Test:

- country
- visa
- pathway
- occupation
- skills assessment
- salary
- qualification
- language
- source
- effective date
- verified date
- legal disclaimer

---

# 20. Frontend QA

For every route:

- access
- route
- loading
- empty
- error
- validation
- API
- persistence
- refresh
- responsive
- production build

---

# 21. Final E2E

```text
Register
→ Login
→ Onboarding
→ Career Passport
→ Career Vault
→ Persona
→ JD import
→ Job DNA
→ Match
→ 60% highlight
→ Skill Gap
→ Resume
→ Truth
→ Application
→ Approval
→ CRM
→ Company
→ Interview
→ Live Interview
→ Remote/Mobility
→ Outcome
→ Analytics
```

---

# 22. Release gate

Use only:

`VERIFIED`

or:

`NOT VERIFIED`

No "almost verified."
