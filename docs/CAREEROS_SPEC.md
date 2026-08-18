# CareerOS — Technical & Functional Specification

## 1. Product Identity

CareerOS is an AI-powered Global Career Operating System.

The immediate objective is a working **Personal Job & Interview Copilot** for one real user, followed by global job intelligence, global mobility and eventually SaaS.

## 2. Version Strategy

See `docs/CAREEROS_VERSION_ARCHITECTURE.md` for the canonical module-by-version allocation.

```text
v0.1 Personal Job & Interview Copilot
v0.2 Global Job Intelligence
v0.3 Global Mobility
v1/v2 SaaS
```

## 3. v0.1 Functional Scope

- Authentication & tenant foundation
- Career Vault
- six default personas + custom persona
- Job Inbox / job discovery
- JD Intelligence
- Job DNA
- Career Ontology foundation
- semantic/capability matching
- mandatory/preferred separation
- Resume Studio
- Truth & Compliance
- Application Factory
- Application CRM
- Company Intelligence
- Interview Intelligence
- Live Interview Assistant
- Web GUI
- basic analytics/outcome tracking
- remote intelligence foundation

## 4. Core Product Principle

CareerOS is career-centric, not job-title-centric.

Career Vault is the factual source of truth.

Jobs become Job DNA.

Matching occurs at capability/evidence level.

The employer's advertised job title is preserved as the application title.

## 5. Career Vault

Authoritative record containing identity/contact, education, employment, responsibilities, projects, achievements, skills, technologies, architecture domains, leadership, certifications, industry/domain, preferences and evidence/provenance.

## 6. Personas

Default:
- Network Architect
- Security Architect
- Cyber Security Architect
- Infrastructure Architect
- Network Manager
- IT Manager
- Custom Persona

Personas change positioning, weighting and presentation without duplicating Career Vault facts.

## 7. Job Discovery

Search must consider advertised title, synonyms, role family, responsibilities, capabilities, technologies, architecture domains, leadership, governance, seniority, industry, transferable skills, location, remote, employment type, salary, work authorization and migration/relocation fit.

A role can be relevant even if its title differs significantly from a persona.

## 8. JD Intelligence and Job DNA

Pipeline:

```text
Source -> Validation -> Normalization -> Canonical JD -> Dedup -> Requirements -> Mandatory/Preferred -> Job DNA -> Retrieval/Embeddings -> Matching -> Explanation
```

Job DNA includes advertised title, role family, seniority, capabilities, technologies, responsibilities, architecture domains, leadership, governance, industry, location, employment model, salary, work authorization constraints, remote constraints, migration/relocation constraints and requirement classes.

## 9. Matching

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

Mandatory failures remain separate from semantic scoring.

Outputs include overall and category scores, matched/partial/missing requirements, hard failures, persona recommendation and explanation.

## 10. Application Title Rule

Example:

```text
Advertised title: Technology Resilience Lead
Persona: Cyber Security Architect
Application title: Technology Resilience Lead
```

## 11. Application Factory

Job -> Persona -> Career Evidence -> JD-to-Evidence Mapping -> Tailored Resume -> ATS Alignment -> Truth & Compliance -> Application Package -> Human Approval -> CRM.

Content may not contain unsupported career facts.

## 12. Company Intelligence

v0.1 requirement. Provide permitted-source company profile, role context, relevant technology/organizational signals, recent relevant developments and interview preparation signals, with source attribution where appropriate.

## 13. Interview Intelligence

v0.1 requirement:
- technical
- architecture
- cybersecurity
- behavioral/leadership
- company
- question prediction
- answer frameworks
- mock interviews
- round tracking
- notes/outcomes

## 14. Live Interview Assistant

v0.1 core requirement.

Architecture boundaries:
- live session
- transcription/input
- question detection
- context retrieval
- Career Vault evidence retrieval
- answer guidance
- notes
- session state
- outcome

Distinguish verified facts, suggested framing, uncertainty and unsupported claims.

## 15. Web GUI

v0.1 core requirement:
- Landing
- Onboarding
- Dashboard
- Career Vault
- Personas
- Job Inbox/Search
- Job Details
- Company Intelligence
- Application Studio
- Applications
- Interview Preparation
- Live Interview Assistant
- Analytics
- Settings

Lovable material is visual reference only.

## 16. Application CRM

```text
DISCOVERED -> ANALYZED -> SHORTLISTED -> READY_FOR_REVIEW -> APPROVED -> APPLIED -> RECRUITER_CONTACT -> INTERVIEW -> OFFER -> ACCEPTED
```

Alternate states: `REJECTED`, `WITHDRAWN`, `ON_HOLD`.

Track recruiter/hiring manager, interviews, notes, reminders, versions and outcomes.

## 17. Remote Intelligence

Evaluate geographic scope, country restrictions, timezone, employment model, EOR/contractor constraints, work authorization, relocation and sponsorship.

## 18. Global Mobility

Structured/versioned rules for country, occupation mapping, skills assessment, sponsorship, salary thresholds, qualifications, language, effective dates and official references. Informational only; not legal advice.

Australia and New Zealand are priority markets.

## 19. AI Orchestration

Logical services/agents include Career Parser, JD Analyzer, Job DNA Generator, Semantic Matcher, Resume Agent, Application Agent, Migration Agent, Interview Agent, Live Interview Assistant, Company Research Agent, Truth Agent and Career Strategy Agent.

Provider abstraction is mandatory.

## 20. Security

Tenant authorization, secure authentication, MFA-ready architecture, secrets externalization, audit logs, file scanning, rate limiting, prompt-injection defenses, SSRF protection, PII minimization and export/deletion controls.

## 21. Non-Functional Direction

Responsive web app, scalable backend, PostgreSQL/pgvector direction, explainable matching, evidence-backed AI, observability, data portability and AI usage tracking.

## 22. Long-Term Modules

See `CAREEROS_VERSION_ARCHITECTURE.md` for the complete final-state module map and version allocation.
