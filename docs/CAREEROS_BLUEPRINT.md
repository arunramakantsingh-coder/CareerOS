# CareerOS — Product & Architecture Blueprint

## 1. Product Position

v0.1: personal job and interview copilot.
v0.2: global job intelligence.
v0.3: global mobility intelligence.
v1/v2: SaaS career operating system.

CareerOS is not primarily a job board, resume template generator or blind auto-apply bot.

## 2. Core Data Flow

```text
Career Vault
    |
    v
Personas
    |
    v
Job Sources / Job Inbox
    |
    v
JD Intelligence
    |
    v
Job DNA
    |
    v
Career Ontology / Evidence Retrieval
    |
    v
Matching
    |
    +--> hard failures
    +--> gaps
    +--> persona recommendation
    +--> opportunity score
    |
    v
Company Intelligence
    |
    v
Application Factory
    |
    v
Human Approval
    |
    v
Application CRM
    |
    +--> Interview Intelligence
    |
    +--> Live Interview Assistant
    |
    v
Outcome / Learning
```

## 3. Career Vault / Evidence Layer

Career Vault stores verified facts. Derived layers include persona positioning, job fit, resumes, applications, interview answers, company preparation and career recommendations. Derived layers must not overwrite source facts.

## 4. Career Ontology

Connect titles, role families, skills, technologies, responsibilities, architecture domains, leadership, governance, industries and capabilities.

This enables title-independent discovery.

## 5. Persona Architecture

```text
Career Vault
   +-- Network Architect
   +-- Security Architect
   +-- Cyber Security Architect
   +-- Infrastructure Architect
   +-- Network Manager
   +-- IT Manager
   +-- Custom Persona
```

## 6. Job Architecture

Every job preserves:

```text
advertised_title
normalized_role_family
```

The advertised title is never replaced.

## 7. Matching Architecture

```text
Eligibility / constraints
        -> Mandatory requirements
        -> Semantic/capability retrieval
        -> Structured scoring
        -> Evidence validation
        -> Explanation
```

Hard failures are explicit.

## 8. Company Intelligence

Reusable context consumed by Job Details, Application Studio, Interview Preparation and Live Interview Assistant. Preserve source attribution and timestamps.

## 9. Interview Architecture

```text
Interview Workspace
 |
 +-- Preparation
 |    +-- company
 |    +-- role
 |    +-- technical
 |    +-- architecture
 |    +-- behavioral
 |
 +-- Mock Interview
 |
 +-- Live Interview Assistant
 |    +-- live input/transcription
 |    +-- question detection
 |    +-- context retrieval
 |    +-- Career Vault evidence
 |    +-- answer guidance
 |    +-- notes
 |
 +-- Outcome
      +-- questions
      +-- performance
      +-- gaps
      +-- next-round preparation
```

## 10. Web GUI Architecture

Use the current Next.js/TypeScript/Tailwind direction, reusable components, typed API client and real backend contracts.

Required v0.1 workflows must be accessible through the GUI.

Lovable exports belong under `design-reference/` and are visual reference only.

## 11. AI Architecture

```text
AI Service Interface
       |
       +-- local model
       +-- cloud model
       +-- future provider
```

Keep domain logic provider-neutral. Prefer deterministic logic -> retrieval -> lightweight model -> stronger model when justified.

## 12. Security Architecture

Cross-cutting security includes authentication, authorization, tenant context, secrets, validation, audit, secure uploads, prompt-injection defense, SSRF defense, privacy controls and rate limiting.

## 13. Connector Architecture

```text
discover(criteria)
fetch(job_reference)
normalize(raw_job)
validate(normalized_job)
deduplicate(job)
health_check()
rate_limit_status()
```

Use only permitted access methods.

## 14. Version Architecture

See `CAREEROS_VERSION_ARCHITECTURE.md` for the canonical version/module matrix. Do not duplicate that matrix here.
