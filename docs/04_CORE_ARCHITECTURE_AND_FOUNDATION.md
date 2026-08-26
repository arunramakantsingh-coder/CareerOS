# CareerOS — Core Architecture & Foundation

## Technology baseline

### Backend

- FastAPI
- Python
- SQLAlchemy
- Alembic
- PostgreSQL
- pgvector-ready architecture
- Docker/Compose

### Frontend

- Next.js
- TypeScript
- Tailwind CSS

### AI

Provider-neutral architecture.

Use:

```text
Deterministic logic
→ retrieval / embeddings
→ fast model
→ stronger model where justified
```

The v0.1 baseline is designed to operate without a paid external AI API for the basic journey; local/provider abstraction may connect to Ollama or another provider later.

Do not replace the technology stack without documented architectural justification.

---

# Stable domain boundaries

```text
Identity / Tenant
Career Passport / Career Vault
Persona Engine
Career Ontology
Job Intelligence
Job DNA
Matching Engine
Skill Gap Intelligence
Resume Studio
Truth & Compliance
Application Factory
Application CRM
Company Intelligence
Interview Intelligence
Live Interview
Remote Intelligence
Global Mobility
AI Orchestration
Analytics / Learning
Web GUI
Security / Governance
```

---

# Career Passport and Career Vault

### Career Passport

The complete professional identity.

### Career Vault

The authoritative evidence-backed source of facts.

Contains:

- identity/contact
- education
- employment
- responsibilities
- projects
- achievements
- skills
- technologies
- architecture
- leadership
- governance
- certifications
- industry/domain
- preferences
- evidence
- provenance
- resume versions

---

# Persona abstraction

Personas all read from the same factual Career Vault.

They alter:

- positioning
- target roles
- capabilities
- scoring weights
- industry
- location
- countries
- salary
- work mode
- presentation

They must not copy and fork candidate facts.

---

# Career Ontology

Normalize and relate:

- titles
- synonyms
- role families
- capabilities
- skills
- technologies
- responsibilities
- architecture domains
- governance
- industries
- leadership
- transferable capabilities

---

# Job pipeline

```text
Source
 ↓
Validate
 ↓
Normalize
 ↓
Canonical Job
 ↓
Deduplicate
 ↓
Extract requirements
 ↓
Mandatory / Preferred
 ↓
Job DNA
 ↓
Embeddings / retrieval
 ↓
Match
 ↓
Explain
 ↓
Skill Gap
 ↓
Rank
```

---

# Job Connector contract

Every connector should provide:

```text
discover(criteria)
fetch(job_reference)
normalize(raw_job)
validate(normalized_job)
deduplicate(job)
health_check()
rate_limit_status()
```

Only lawful/permitted access methods.

---

# Core data model

The specification defines:

- User
- Tenant
- CareerProfile
- Employment
- Project
- Skill
- Technology
- Certification
- Achievement
- Evidence
- Persona
- JobSource
- Job
- JobDNA
- JobMatch
- Resume
- Application
- Recruiter
- Interview
- Offer
- Country
- Visa
- MigrationRule
- MigrationProfile
- Subscription
- AuditLog

The reconciled code additionally contains concrete models around:

- capability taxonomy
- job discovery/listing/skill/responsibility
- match dimensions/recommendations
- persona skill weights
- remote eligibility
- resume sections/evidence links
- occupation mapping
- migration pathway/profile/rule
- v0.1 Application / CompanyIntelligence / Interview / TruthCheck / AuditLog / LiveInterviewSession

---

# Migration chain

The reconciled project contains:

```text
001 initial schema
002 career vault
003 persona engine
004 job intelligence
005 match engine
006 resume AI
007 job source connector
008 semantic discovery
009 remote eligibility
010 migration engine
011 authentication foundation
012 v0.1 product
```

Every future DB change needs a new migration.

Never rewrite an applied migration.

---

# API/domain surfaces present in the reconciled project

Existing backend API areas include:

- auth
- health
- discovery
- jobs
- job sources
- matches
- personas
- persona weights
- resumes
- remote
- migration
- v0.1 product
- career profile/evidence
- applications
- companies
- interviews
- live interview
- analytics

The actual runtime state of each endpoint must be tested; existence is not proof.

---

# Security architecture

Cross-cutting security includes:

- tenant-scoped authorization
- authentication
- RBAC
- secure secrets
- validation
- secure uploads
- file scanning
- PII minimization
- audit logs
- rate limiting
- SSRF protection
- prompt-injection defenses
- secure OAuth-ready architecture
- encryption
- user export/deletion
- explicit consent for model-training use

---

# Multi-tenancy

Never trust a client-provided tenant identifier.

Derive tenant context from authenticated identity/token claims.

Every user-owned query must enforce tenant ownership.

Minimum security matrix:

```text
User A → Tenant A = ALLOW
User A → Tenant B = DENY
User B → Tenant B = ALLOW
```

Apply this to:

- Career Vault
- Personas
- Jobs
- Matches
- Skill Gaps
- Resumes
- Applications
- Interviews
- Companies
- Mobility
- Analytics
- Audit data

---

# Observability

At minimum:

- structured logging
- request/correlation IDs
- readiness/liveness
- error tracking
- metrics
- audit events
- AI usage/cost metrics

Do not log secrets or sensitive payloads unnecessarily.

---

# Architecture decision rule

Do not create parallel competing implementations simply because they are easier.

Prefer:

```text
EXTEND → REFACTOR → FIX
```

over:

```text
DELETE → REBUILD
```

unless the existing implementation is fundamentally incompatible.
