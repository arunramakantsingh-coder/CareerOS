# CareerOS — Technical & Functional Specification

## Product
CareerOS — AI-Powered Global Career Operating System.

Target: web-based multi-tenant SaaS for job seekers, international career movers and executives.

## Functional Modules
- Authentication & Tenant: sign-up, login, password reset, OAuth-ready architecture, profile, tenant isolation, consent/security.
- Career Vault: CV import, career parsing, employment, skills, projects, certifications, achievements, evidence.
- Persona Manager: personas, target roles, countries, salary, work mode, industries, priorities.
- Job Discovery: connectors, ingestion, normalization, deduplication, search, saved jobs.
- JD Intelligence: JD parsing, requirements, role family, seniority, Job DNA.
- Matching: technical, experience, seniority, leadership, industry, location, salary, remote, migration.
- Resume Studio: persona selection, evidence retrieval, tailored resume, version comparison, truth validation.
- Application Factory: cover letter, application answers, recruiter messages, review and approval.
- Application CRM: pipeline, recruiters, interviews, offers, rejection, notes, reminders, versions.
- Company Intelligence: company profile, role context, technology signals, recruiter/hiring manager information.
- Interview AI: question prediction, personalized preparation, mock interview, round tracking.
- Global Mobility: country profiles, migration rules, eligibility, sponsorship and relocation.
- Remote Intelligence: scope, restrictions, timezone, employment model, eligibility.
- Analytics: funnel, source performance, persona performance, conversion and recommendations.
- Billing: plans, entitlements and usage; payment can be deferred.

## Core Data Model
User, Tenant, CareerProfile, Employment, Project, Skill, Technology, Certification, Achievement, Evidence, Persona, JobSource, Job, JobDNA, JobMatch, Resume, Application, Recruiter, Interview, Offer, Country, Visa, MigrationRule, MigrationProfile, Subscription, AuditLog.

## Job Connector Contract
Every connector supports:
`discover(criteria)`, `fetch(job_reference)`, `normalize(raw_job)`, `validate(normalized_job)`, `deduplicate(job)`, `health_check()`, `rate_limit_status()`.

## Job Processing
1. Receive permitted job source data.
2. Validate minimum fields.
3. Normalize title/company/location/salary/work mode.
4. Canonicalize JD.
5. Compute duplicate fingerprint.
6. Merge duplicates while retaining source references.
7. Extract requirements.
8. Separate mandatory/preferred.
9. Generate Job DNA.
10. Generate embeddings where useful.
11. Store searchable representation.
12. Match against personas.
13. Generate explanations/gaps.
14. Rank opportunity.

## Job DNA
Role family, seniority, capabilities, technologies, responsibilities, architecture domains, leadership, governance, industry, location, employment model, salary and constraints.

## Matching
Initial configurable model:
- Technical/capability 25%
- Relevant experience 20%
- Architecture/domain 15%
- Leadership/seniority 10%
- Industry/domain 10%
- Location/remote 5%
- Salary 5%
- Migration/relocation 5%
- Certification/qualification 5%

Mandatory failure is separate from semantic score.

## Match Output
Overall, career, technical, experience, seniority, location, salary, remote and migration scores; matched, partial and missing requirements; hard failures; recommended persona; human-readable explanation.

## Resume Workflow
Select job/persona → retrieve evidence → JD-to-evidence mapping → draft → ATS alignment → Truth Agent → flag unsupported claims → approved content → immutable version.

## Truth & Compliance
Every material claim maps to evidence. Dates, technologies and certifications must be supported. No invented metrics, employers, projects or unsupported experience.

## Application State
DISCOVERED → ANALYZED → SHORTLISTED → READY_FOR_REVIEW → APPROVED → APPLIED → RECRUITER_CONTACT → INTERVIEW → OFFER → ACCEPTED. Alternate: REJECTED, WITHDRAWN, ON_HOLD.

## Global Mobility
Migration rules are structured/versioned data. Support occupation mapping, skills assessment, points/rules, salary thresholds, sponsorship, qualifications, language, effective dates and official references.

Australia/New Zealand support occupation classification, skills assessment, employer sponsorship, points pathways where applicable, state/regional pathways, salary/occupation constraints, English/qualification factors, job-to-occupation compatibility and versioned rules.

## Remote Intelligence
Determine geographic scope, timezone compatibility, employment model, country restrictions, relocation requirement and remote fit.

## AI Orchestration
Career Parser, JD Analyzer, Semantic Matcher, Resume Agent, Application Agent, Migration Agent, Interview Agent, Company Research Agent, Truth Agent and Career Strategy Agent.

Use deterministic parsing where possible, embeddings for first-stage retrieval, fast models for classification/extraction, stronger models for shortlisted generation, caching and selective evidence retrieval.

## Security
Tenant-scoped authorization, encryption, MFA-ready architecture, secure OAuth, externalized secrets, audit logs, file scanning, rate limiting, prompt-injection defenses, SSRF protection, PII minimization, export/deletion and explicit consent for model-training use.

## APIs
/auth, /career, /personas, /jobs, /matches, /resumes, /applications, /interviews, /companies, /mobility, /sources, /analytics, /billing.

## UI
Landing, Onboarding, Dashboard, Career Vault, Personas, Job Search, Job Details, Application Studio, Applications, Interviews, Global Mobility, Analytics and Settings.

## MVP Acceptance
A user can create an account, import a CV, obtain a structured Career Vault, create at least five personas, analyze a JD, generate Job DNA, match semantically/structurally, understand why it matched, see gaps/hard failures, generate a JD-specific resume, trace material claims to evidence, review/approve an application package, track applications, distinguish international remote restrictions and support future migration modules without core redesign.

## Non-Functional
99.5% MVP availability target, 2–3 second common interactions excluding AI generation, scalable backend, OWASP-aligned security, logs/metrics/error tracking/audit logs, data portability, explainable matching and AI usage tracking.

## Final Principle
CareerOS must remain career-centric, not job-title-centric. Career Vault/Career Graph is the source of truth; jobs become Job DNA; matching occurs at capability/evidence level; applications are evidence-backed; global mobility is a connected decision layer.
