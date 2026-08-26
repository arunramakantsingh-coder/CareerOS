# CareerOS — Domain Modules & Delivery Framework

## Delivery contract

Every module has:

```text
Database
→ Backend API
→ Domain/AI logic
→ Frontend UI
→ Automated tests
→ Integration/E2E evidence
```

If a UI is required, the backend feature is not accepted without corresponding UI integration.

---

# M1 — Identity & Tenant Foundation

### Required

- registration
- login
- password hashing
- JWT
- current user
- tenant context
- protected APIs
- tenant isolation
- auth tests

### UI

- Login
- Signup
- onboarding shell
- auth state
- protected navigation

### Gate

User/tenant isolation and runtime auth are proven.

---

# M2 — Career Vault / Career Passport

### Required

- CV import
- career parsing
- unified candidate record
- employment
- education
- skills
- technologies
- certifications
- projects
- achievements
- evidence
- provenance
- editing

### UI

- Career Passport
- Career Vault
- Evidence
- Upload/import
- completeness

### Gate

Real career data persists and can be retrieved safely.

---

# M3 — Persona Engine

### Required

- default personas
- custom persona
- create/update/delete
- activate
- clone
- skill weighting
- target roles
- countries
- industries
- salary
- work mode

### UI

- persona list
- detail
- weights
- active persona

### Gate

Personas share facts rather than duplicating Career Vault content.

---

# M4 — Job Inbox / JD Intelligence

### Required

- manual JD import
- source
- canonical job
- deduplication
- parser
- role family
- seniority
- requirements
- mandatory/preferred
- responsibility extraction
- company
- location
- remote
- salary
- authorization/sponsorship metadata

### UI

- Jobs
- Import
- Job Details
- JD Intelligence

### Gate

A real JD becomes structured job data.

---

# M5 — Career Ontology / Job DNA

### Required

- capability taxonomy
- title/synonym normalization
- role family
- Job DNA
- architecture domain
- leadership
- governance
- industry
- constraints

### UI

Explainable Job DNA.

### Gate

Title-dissimilar but capability-relevant roles can be represented correctly.

---

# M6 — Matching Engine

### Required

- structured matching
- capability/evidence match
- configurable weights
- hard failures
- recommended persona
- explanation

### Baseline scoring

- technical/capability 25%
- experience 20%
- architecture/domain 15%
- leadership/seniority 10%
- industry/domain 10%
- location/remote 5%
- salary 5%
- migration/relocation 5%
- certification/qualification 5%

Mandatory failures are separate from the semantic score.

---

# M7 — Skill Gap Intelligence

### Required

- per-job observation
- matched/partial/missing
- mandatory/preferred
- persona
- evidence
- cumulative aggregation
- frequency
- priority
- trend
- learning status

### UI

- job-level missing skills
- cumulative Skill Gap dashboard
- top recurring gaps
- mandatory gap frequency
- persona impact
- role-family impact
- learning status

### Gate

Repeated analyzed jobs produce persistent cumulative data.

---

# M8 — Resume Studio + Truth

### Required

```text
Job
→ Persona
→ Evidence
→ JD-to-evidence
→ Resume
→ ATS alignment
→ Truth Agent
→ Immutable version
```

### Gate

Unsupported material claims are blocked/flagged.

---

# M9 — Application Factory

Required:

- cover letters
- application answers
- recruiter messages
- hiring-manager messages
- approval
- versioning
- truth gate

---

# M10 — Application CRM

Required states:

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

Alternates:

- REJECTED
- WITHDRAWN
- ON_HOLD

Track recruiter, interview, offer, notes, reminders and resume versions.

---

# M11 — Company Intelligence

Required:

- company profile
- role context
- technology signals
- recruiter/hiring context
- source attribution
- timestamp
- confidence

---

# M12 — Interview Intelligence

Required:

- technical
- architecture
- behavioral
- company
- role
- question prediction
- answer preparation
- mock interview
- round tracking
- notes
- outcome
- gap analysis

---

# M13 — Live Interview Assistant

Required:

```text
Interview context
→ question input/transcription
→ context retrieval
→ Career Vault evidence
→ response guidance
→ user control
```

Never fabricate career experience.

---

# M14 — Remote Intelligence

Evaluate:

- worldwide
- country restricted
- India-only
- US-only
- EU/EEA
- APAC/EMEA
- timezone
- employment model
- work authorization
- contractor/EOR
- relocation
- sponsorship

---

# M15 — Global Mobility

Initial country order:

1. Australia
2. New Zealand
3. UAE
4. Qatar
5. Saudi Arabia
6. Singapore
7. UK
8. Canada
9. Germany/EU

Use versioned official migration rules.

---

# M16 — Analytics / Learning

Track:

- discovered
- shortlisted
- applications
- interviews
- offers
- acceptance
- rejection
- persona performance
- source performance
- country
- salary
- capability
- skill gaps
- successful positioning

---

# M17 — Web GUI Integration

Every major backend capability must have a real frontend surface.

Required v0.1 workflows:

- landing
- login
- onboarding
- dashboard
- Career Passport
- Career Vault
- personas
- jobs
- job details
- application studio
- applications
- interviews
- live interview
- global mobility
- analytics
- settings

---

# Module completion matrix

| Module | DB | API | AI/Domain | UI | Tests | E2E |
|---|---|---|---|---|---|---|
| Identity/Tenant | yes | yes | yes | yes | yes | yes |
| Career Vault | yes | yes | yes | yes | yes | yes |
| Personas | yes | yes | yes | yes | yes | yes |
| Job/JD | yes | yes | yes | yes | yes | yes |
| Job DNA | yes | yes | yes | yes | yes | yes |
| Matching | yes | yes | yes | yes | yes | yes |
| Skill Gap | yes | yes | yes | yes | yes | yes |
| Resume/Truth | yes | yes | yes | yes | yes | yes |
| Application | yes | yes | yes | yes | yes | yes |
| CRM | yes | yes | yes | yes | yes | yes |
| Company | yes | yes | yes | yes | yes | yes |
| Interview | yes | yes | yes | yes | yes | yes |
| Live Interview | yes | yes | yes | yes | yes | yes |
| Remote | yes | yes | yes | yes | yes | yes |
| Mobility | yes | yes | yes | yes | yes | yes |
| Analytics | yes | yes | yes | yes | yes | yes |
