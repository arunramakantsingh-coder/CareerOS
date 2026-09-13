# CareerOS — Master Product Roadmap & Control Document
Version: 0.2-Reconciled
Status: AUTHORITATIVE PRODUCT DIRECTION

## Product Vision
CareerOS is an **AI-Powered Global Career Operating System** and personal AI Career Agent.

> Provide career information once → build a trusted Career Vault → generate market-aware personas → continuously discover global opportunities → analyze/rank jobs → explain fit and skill gaps → assist applications → track outcomes → learn.

CareerOS is not merely a job board, resume builder, or blind auto-apply bot.

## Product Priority Order
1. Foundation and working application shell
2. Authentication / identity
3. Career Vault and candidate intelligence
4. Multiple-CV ingestion and normalization
5. Dynamic personas
6. Global job discovery
7. Email/job-alert intelligence
8. Company and recruiter intelligence
9. Job normalization/deduplication/Job DNA
10. Matching and explainability
11. 60%+ job highlighting
12. Cumulative missing-skill intelligence
13. Application Factory / human-in-the-loop assistance
14. Application CRM
15. Remote intelligence
16. Interview intelligence / live interview assistant
17. Analytics and continuous learning
18. Global Mobility / visa / migration intelligence
19. Advanced automation, SaaS hardening and monetization

Global Mobility is deliberately later than the core job-hunting loop.

## Product Engines
- Career Intelligence Engine
- Persona Engine
- Job Intelligence Engine
- Matching Engine
- Application Factory
- Global Mobility Engine
- Career CRM & Outcome Engine

## Global Intelligence Engine — Platform Architecture

The **Global Intelligence Engine** is a platform-level, provider-neutral service used by all CareerOS AI workloads. It is not a CV-only feature, not a personal-user setting, and not a collection of direct vendor integrations inside individual modules.

### Canonical flow
```text
CareerOS module
    ↓
CareerOS Intelligence Service
    ↓
Global Intelligence Gateway / Router
    ↓
Provider adapter
    ↓
Selected model/provider
```

All AI-processing modules must use this path, including:
- CV/profile ingestion and reconciliation
- document intelligence and evidence understanding
- profile completeness and reconciliation intelligence
- persona generation
- job/JD intelligence and Job DNA
- matching, scoring and recommendations
- skill-gap intelligence
- company and recruiter intelligence
- research and global opportunity intelligence
- application assistance
- interview preparation and interview intelligence
- future career planning, notifications and AI capabilities

**Rule:** Product modules must not call OpenAI, Gemini, Claude, OpenRouter, Ollama, Mistral, xAI, Groq, DeepSeek or another AI vendor directly. Vendor-specific code belongs behind the Intelligence Gateway.

### Provider-neutral registry
The platform must support multiple local and paid providers without changing consuming modules. The initial provider catalog includes:
- Ollama
- OpenRouter
- OpenAI
- Google Gemini
- Anthropic Claude
- Mistral AI
- xAI
- Groq
- DeepSeek

Provider/model selection is an Intelligence Engine policy, not frontend business logic. Providers expose normalized request/response contracts through adapters.

### Persistent credentials
Provider credentials are **global platform configuration**, not user career data.

Requirements:
- credentials stored encrypted at rest
- API secrets never returned to the browser/API responses
- UI exposes only configured state and limited key metadata such as last four characters
- Save Credentials is separate from Activate Provider
- activating a previously configured provider must never require re-entering its API key
- a dedicated production encryption secret must be supported
- local development may safely derive encryption from the existing application secret when no dedicated key is configured
- future integrations may move secret storage to a managed secret store without changing the provider contract

### Provider lifecycle
```text
Not configured
      ↓
Save Credentials
      ↓
Configured
      ↓
Test Connection
      ↓
Activate Provider
      ↓
Global Active Provider
```

Saving configuration does **not** implicitly change the active provider. Activation is explicit.

### Routing and fallback
The engine is designed for task-based routing rather than one permanent model for every workload. Future routing policy must consider:
- task/capability
- model quality and reasoning strength
- structured-output support
- privacy requirements
- health and availability
- latency
- rate limits/quota
- cost
- context requirements
- fallback policy

The first implementation establishes the global provider registry and explicit activation boundary; advanced automatic routing/fallback remains a controlled extension and must not be presented as implemented before runtime support exists.

### Global multi-user boundary
The Intelligence Engine serves the CareerOS platform and therefore supports many authorized users. Provider configuration is global/platform-level while career context remains tenant/user scoped.

AI processing must never cross user/tenant boundaries. The engine is not the system of record: structured profile, career, evidence, job or application changes remain controlled by CareerOS application services, validation, provenance and human-approval rules.

### Project Control ownership
Global Intelligence configuration belongs under:

```text
Project Control
└── Global Intelligence Engine
    ├── Overview
    ├── Providers
    ├── Models
    ├── Routing
    ├── Fallback
    ├── Usage & Cost
    ├── Health / Latency / Quota
    ├── Credentials
    └── Policies
```

Only authorized developer/admin users may manage platform AI credentials and activation. Normal users consume the resulting intelligence capabilities without seeing platform secrets.

### Future operational controls
The architecture should leave room for:
- per-task routing policies
- provider/model health monitoring
- latency and failure metrics
- token and cost accounting
- quota/rate-limit controls
- provider fallback chains
- model capability discovery
- data residency/privacy policies
- audit history and credential rotation
- tenant-aware usage/entitlements for future SaaS

These are planned controls unless explicitly implemented and verified.

## Functional Stages

### Stage 0 — Foundation & Control
Repository, Docker, PostgreSQL/pgvector, FastAPI, Next.js, Git, testing, AI-to-AI coordination.

### Stage 1 — Application Shell & Identity
Working frontend/backend, navigation, registration/login, sessions, protected routes and provider authentication.

### Stage 2 — Career Vault & CV Intelligence
Multiple CVs, parsing, structured extraction, normalization, deduplication, provenance and candidate editing.

### Stage 3 — Dynamic Personas
AI-generated market personas based on evidence, capabilities, experience, responsibilities and market terminology.

### Stage 4 — Global Job Discovery
Extensible source registry and connectors for job portals, company career pages, staffing sources and public sources.

### Stage 5 — Email Intelligence
Authorized email integration; identify job alerts, recruiter messages, interviews, acknowledgements, rejections and recommendations; convert relevant messages to structured jobs.

### Stage 6 — Company & Recruiter Intelligence
Resolve original company vacancy, recruiter, hiring manager, agency and contact information.

### Stage 7 — Job Intelligence & Matching
Normalize jobs, deduplicate, extract Job DNA, match against Career Vault + personas + preferences and explain the score.

### Stage 8 — Skill Gap Intelligence
Highlight jobs at/above 60% match and show missing skills, experience gaps and mandatory requirement gaps. Persist per-job observations and cumulative skill-gap aggregates.

### Stage 9 — Application Factory
Generate truthful job-specific CV/application materials, assisted form filling and human approval workflows.

### Stage 10 — Application CRM
Track discovered → analyzed → matched → recommended → approved → applied → acknowledged → interview → offer → closed.

### Stage 11 — Remote Intelligence
Determine remote eligibility, geography, timezone, work authorization, contractor/EOR and location restrictions.

### Stage 12 — Interview Intelligence
Interview preparation plus live interview assistance. Live assistance should favor compact actionable cues rather than long paragraphs.

### Stage 13 — Analytics & Continuous Learning
Source performance, persona performance, conversion, missing skills, rejection patterns, market demand and outcome learning.

### Stage 14 — Global Mobility
Visa, sponsorship, relocation, country comparison and migration pathways.

### Stage 15 — Production/SaaS Hardening
Subscriptions, advanced automation, multi-tenant hardening, observability, compliance and broader coverage.

## Job Sources
The architecture must be extensible and cover, as applicable:
- LinkedIn
- Naukri
- Indeed
- Glassdoor
- Foundit/Monster
- Dice
- ZipRecruiter
- Wellfound
- NaukriGulf
- Bayt
- GulfTalent
- FlexJobs
- SEEK Australia
- SEEK New Zealand
- Trade Me Jobs
- Jora
- Remote OK
- We Work Remotely
- Remotive
- Staffing/recruitment portals
- Company career portals
- Government/public job portals
- Recruiter sources
- Authorized email feeds

Prefer official APIs/feeds where available; preserve source provenance and deduplicate.

## Canonical Job
Multiple discoveries of the same vacancy become one Canonical Job Record while retaining all sources. Prefer the original company vacancy where available.

## Matching & 60% Highlight Rule
Every job receives an explainable score covering overall match, skills, experience, architecture/domain, seniority, industry, location, remote fit, compensation and mandatory requirements.

**Rule:** `overall/profile match >= 60%` → highlight the job.

A highlighted card MUST show:
- Why it matches
- Matching skills
- Missing skills
- Experience gaps
- Mandatory requirement gaps
- Applicable persona(s)
- Recommendation

60% is a highlight threshold, not automatic application approval.

## Cumulative Missing Skills
Persist per-job skill-gap observations and aggregate them across jobs, e.g.:

```text
Kubernetes  7 jobs
Terraform   5 jobs
AWS         4 jobs
```

Support analysis by skill, persona, job family, industry, geography, seniority and time period. The purpose is to show what the candidate should strengthen.

## Authentication & Identity
Authentication is a first-class foundation.

Target login options:
- Email/password
- Google OAuth/OIDC
- LinkedIn OAuth/OIDC
- Facebook OAuth/OIDC
- Additional OIDC providers later
- MFA capability

The Product Blueprint specifies Firebase Authentication or an equivalent managed identity service, plus MFA, audit logs, least privilege, encryption, secrets management and user-controlled deletion/export.

Provider-specific implementation must be selected during the Identity milestone. Never hard-code provider secrets.

CareerOS authentication answers **who the user is**. External account authorization answers **what data the user has explicitly authorized CareerOS to access** (e.g. email).

One person may link multiple providers to one internal CareerOS user; avoid duplicate accounts.

## Human-in-the-Loop
### Manual
AI searches, analyzes, scores and recommends.

### Assisted
AI prepares/fills; user reviews and approves.

### Automatic
AI submits only according to explicit user-defined rules.

CareerOS must never fabricate candidate information.

## UI Is Part of the Feature
A backend feature is not complete when the product requires a user-facing capability and the UI is absent or disconnected.

Required flow:
Backend → API → Frontend → UI → Runtime test → Evidence.

## Milestone Definition of Done
```text
IMPLEMENTED
  ↓
EXECUTED
  ↓
ACTUAL EVIDENCE
  ↓
QA REVIEWED
  ↓
RUNTIME/UI ACCEPTED BY ARUN
  ↓
STABILITY GATE
  ↓
MILESTONE VERIFIED
  ↓
NEXT MILESTONE AUTHORIZED
```

Every milestone must check Docker services, PostgreSQL, backend health, frontend health, ports, APIs, UI, changed-module tests, regression, database state, logs and Git state.

## Truth Principle
CareerOS may rewrite/summarize verified information but must not fabricate employers, certifications, technologies, projects, dates, achievements, experience, authorization or application answers.
