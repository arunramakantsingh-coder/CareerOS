# CareerOS — Development Roadmap

## 1. Development Model

Use `AGENTS.md` + current project MD files + one current task.

Complete one vertical task, test it, review it, document it, then move to the next.

Do not optimize for phase count. Optimize for a working end-to-end user outcome.

## 2. Version Growth

```text
v0.1 Personal Job & Interview Copilot
        ->
v0.2 Global Job Intelligence
        ->
v0.3 Global Mobility
        ->
v1/v2 SaaS
```

## 3. v0.1 Vertical Slices

### Slice 0 — Documentation & Repository Alignment
- align MD control plane
- define version/module architecture
- define AI/human/GitHub workflow
- define safe-upload policy
- define PowerShell-first implementation
- establish design-reference boundary

### Slice 1 — Repository Verification
- assess `main`
- verify dependencies/builds
- verify database/migrations
- verify APIs
- verify frontend build
- establish baseline test evidence

### Slice 2 — Career Vault + Personas
- usable Career Vault
- CV import
- evidence/provenance
- six default personas
- custom persona
- persona weights

### Slice 3 — Job Inbox + JD Intelligence
- permitted/manual job import
- Job Inbox
- parsing
- role family
- capabilities
- responsibilities
- technologies
- mandatory/preferred requirements

### Slice 4 — Job DNA + Matching
- Job DNA
- ontology foundation
- evidence retrieval
- configurable scoring
- hard failures
- explanations
- persona recommendation

### Slice 5 — Application Factory
- JD-to-evidence mapping
- tailored resume
- ATS alignment without keyword stuffing
- Truth & Compliance
- cover letter
- answers
- recruiter messages
- human approval

### Slice 6 — Application CRM
- state machine
- recruiters/hiring managers
- interviews
- notes
- offers
- outcomes
- version history

### Slice 7 — Company Intelligence
- permitted research
- company profile
- role context
- relevant technology/organizational signals
- recruiter/hiring context where permitted
- interview themes

### Slice 8 — Interview Intelligence
- technical
- architecture
- cybersecurity
- behavioral/leadership
- company preparation
- question prediction
- mock interview
- round tracking

### Slice 9 — Live Interview Assistant
- live session
- transcription/input
- question detection
- retrieval
- evidence retrieval
- answer guidance
- notes
- post-interview outcome

### Slice 10 — Web GUI
- dashboard
- Career Vault
- personas
- Job Inbox
- Job Details
- Company Intelligence
- Application Studio
- Applications
- Interview Preparation
- Live Interview Assistant
- Analytics
- Settings

### Slice 11 — v0.1 End-to-End Validation

```text
Career Vault -> Persona -> Job -> JD -> Job DNA -> Match -> Company Intelligence -> Application -> Truth -> Approval -> Interview -> Live Assistant -> Outcome
```

## 4. v0.2 — Global Job Intelligence

- permitted global connectors
- feeds/APIs/employer pages
- global normalization/deduplication
- remote intelligence
- global ranking
- recruiter/company intelligence expansion
- source analytics
- capability/role clustering
- Global Opportunity Score

## 5. v0.3 — Global Mobility

Priority:
1. Australia
2. New Zealand
3. UAE
4. Qatar
5. Saudi Arabia
6. Singapore
7. UK
8. Canada
9. Germany/EU

Deliver versioned official migration rules, occupation mapping, skills assessment, sponsorship, salary/qualification/language factors and relocation feasibility.

## 6. v1/v2 — SaaS

- subscriptions
- entitlements
- usage governance
- billing
- advanced automation
- recruiter/coach/B2B
- partner integrations
- production scale

## 7. Out-of-Sequence Restrictions

Do not delay v0.1 for broad SaaS marketing, mass connector coverage, country-wide immigration rules, speculative infrastructure or large analytics systems.

## 8. Completion Rule

A slice is complete only when implementation exists, relevant tests/builds pass, the workflow works, GitHub reflects the change, documentation is current and no known critical regression remains.
