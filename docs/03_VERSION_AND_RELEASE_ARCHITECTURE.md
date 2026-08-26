# CareerOS — Version & Release Architecture

## Stable repository principle

CareerOS grows vertically from the same repository.

```text
v0.1
 ↓
v0.2
 ↓
v0.3
 ↓
v1/v2
```

Later releases extend the same architecture.

Do not create parallel product repositories for each version.

---

# v0.1 — Personal Job & Interview Copilot

## Goal

Deliver a useful personal career system.

### Core scope

- authentication / tenant foundation
- onboarding foundation
- Career Passport / Career Vault
- personas
- job/JD import
- JD Intelligence
- Job DNA
- career ontology foundation
- matching
- hard requirement failures
- 60% Skill-Match Opportunity Highlight
- Skill Gap Intelligence foundation
- Resume Studio
- Truth & Compliance
- Application Factory
- Application CRM
- Company Intelligence
- Interview Intelligence
- Live Interview foundation
- Remote Intelligence foundation
- Analytics foundation
- real Next.js GUI

## Explicit v0.1 non-goals

Do not make v0.1 depend on:

- commercial billing
- mass scraping
- enterprise infrastructure
- broad B2B
- massive global connector ecosystem
- full immigration decision engine
- recruiter marketplace

---

# v0.2 — Global Job Intelligence

## Focus

Move from a personal copilot to a global opportunity-intelligence engine.

### Core additions

- global source framework
- capability discovery
- semantic discovery
- Career Capability Graph
- expanded Job DNA
- remote eligibility
- timezone intelligence
- relocation intelligence
- salary intelligence
- sponsorship matching
- country opportunity ranking
- global job-source expansion
- original employer vacancy resolution

### UI

Visible from v0.1 as a versioned/planned surface; implemented progressively.

---

# v0.3 — Global Mobility

## Focus

Make migration a first-class career decision layer.

### Initial markets

1. Australia
2. New Zealand
3. UAE
4. Qatar
5. Saudi Arabia
6. Singapore
7. UK
8. Canada
9. Germany/EU

### Requirements

- occupation mapping
- skills assessment
- eligibility
- sponsorship
- salary/qualification/language factors
- pathways
- effective dates
- official source references
- legal disclaimer
- versioned rules

---

# v1/v2 — SaaS

Future:

- subscriptions
- entitlements
- usage limits
- advanced automation
- broader global coverage
- executive features
- recruiter/coach features
- B2B opportunities

---

# Git release model

Conversation-confirmed release control:

```text
release/v0.1-personal-job-interview-copilot
        ↓
v0.1.0
        ↓
release/v0.2-global-job-intelligence
```

The v0.1.0 tag is the frozen v0.1 baseline.

The v0.2 branch was created from that v0.1.0 baseline.

## Rule

Never rewrite a released branch/history without explicit owner approval.

Use focused feature commits and release tags.

---

# UI versioning rule

The UI should show:

```text
CURRENT
v0.1 Personal Job & Interview Copilot

NEXT
v0.2 Global Job Intelligence

FUTURE
v0.3 Global Mobility
```

Future items can be visible as architecture/roadmap, but no fake behavior.

---

# Release gate

A version is not released because files exist.

A release is accepted only after:

- code review
- DB/migration review
- backend tests
- frontend build
- API smoke tests
- UI tests
- security tests
- tenant tests
- critical E2E
- documentation update
- known issues reviewed

Result must be:

`VERIFIED` or `NOT VERIFIED`.
