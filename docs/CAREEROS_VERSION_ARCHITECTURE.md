# CareerOS — Version Architecture & Long-Term Evolution

## 1. Purpose

This is the canonical map of how CareerOS evolves from the immediate personal product into the final SaaS platform.

It answers:
1. What is CareerOS ultimately intended to become?
2. Which modules belong to each version?
3. Which modules are introduced, expanded or deferred at each version?
4. How does each version build on the previous version without unnecessary redesign?

Consult this file before moving functionality between versions.

## 2. Final Product Vision

CareerOS evolves into a career operating system connecting:

```text
Career Vault
    ->
Career Intelligence / Evidence Graph
    ->
Personas
    ->
Global Job Intelligence
    ->
Job DNA
    ->
Matching
    ->
Remote / Company / Mobility Intelligence
    ->
Application Factory
    ->
Truth & Compliance
    ->
Application CRM
    ->
Interview Intelligence
    ->
Live Interview Assistant
    ->
Outcome Learning
    ->
Career Strategy
    ->
SaaS Platform
```

The end state is not merely a job board or resume builder. It is a continuously useful career decision, application and interview system.

## 3. Version Strategy

```text
CareerOS
   |
   +-- v0.1 Personal Job & Interview Copilot   <- NOW
   |
   +-- v0.2 Global Job Intelligence
   |
   +-- v0.3 Global Mobility
   |
   +-- v1/v2 SaaS
```

## 4. Version Responsibility Matrix

| Module | v0.1 | v0.2 | v0.3 | v1/v2 |
|---|---|---|---|---|
| Authentication & Tenant | Core | Harden | Scale | SaaS multi-user |
| Career Vault | Core | Enrich | Enrich | Multi-user ecosystem |
| Evidence/Provenance | Core | Expand | Expand | Advanced graph |
| Personas | Core | Expand | Expand | Shared/team personas |
| Career Ontology | Foundation/Core | Global expansion | Mobility mappings | Global ontology |
| Job Discovery/Inbox | Core/manual+permitted | Global connectors | Global expansion | Marketplace-scale |
| JD Intelligence | Core | Global scale | Mobility-aware | Continuous intelligence |
| Job DNA | Core | Global/industry depth | Occupation compatibility | Advanced ontology |
| Matching | Core | Global opportunity score | Career+mobility score | Predictive optimization |
| Remote Intelligence | Basic | Core | Mobility-integrated | Advanced employment intelligence |
| Company Intelligence | Core | Expanded | Mobility/recruiter context | Continuous company graph |
| Recruiter Intelligence | Basic where permitted | Core | Expanded | Advanced |
| Resume Studio | Core | Advanced | Mobility-aware | Continuous optimization |
| Truth & Compliance | Core | Advanced | Mobility/legal-source separation | Enterprise governance |
| Application Factory | Core | Automated assistance | Country-aware | Advanced automation |
| Application CRM | Core | Analytics | Global outcomes | Full career CRM |
| Interview Intelligence | Core | Advanced | Country/company context | Continuous learning |
| Live Interview Assistant | Core | Advanced | Global/role context | Advanced real-time copilot |
| Analytics | Basic | Core | Global/mobility | Advanced analytics |
| Global Mobility | Foundation/preview | Basic signals | Core | Advanced |
| Migration Intelligence | Foundation only | Foundation | Core | Advanced |
| Web GUI | Core | Expand | Expand | SaaS UX |
| Integrations/Connectors | Manual/permitted | Many permitted sources | Mobility sources | Partner ecosystem |
| AI Orchestration | Foundation | Cost/routing | Advanced | Multi-provider scale |
| Billing | Architecture only | Architecture | Architecture | Core |
| SaaS Entitlements | Foundation | Foundation | Foundation | Core |
| B2B/Recruiter/Coach | Not priority | Explore | Design | Core |

## 5. v0.1 — Personal Job & Interview Copilot

### Objective

Make CareerOS personally useful before building a broad platform.

### Core modules

1. Identity/Auth and tenant foundation
2. Career Vault
3. Persona Engine
4. Job Inbox / permitted/manual discovery
5. JD Intelligence
6. Job DNA
7. Career Ontology foundation
8. Matching Engine
9. Resume Studio
10. Truth & Compliance
11. Application Factory
12. Application CRM
13. Company Intelligence
14. Interview Intelligence
15. Live Interview Assistant
16. Web GUI
17. Basic Analytics / outcome tracking
18. Remote Intelligence foundation

### v0.1 should intentionally defer

- mass scraping or account automation
- broad global connector coverage
- full immigration decision engine
- commercial billing
- broad B2B features
- enterprise-scale infrastructure

## 6. v0.2 — Global Job Intelligence

### Objective

Turn the personal copilot into a global opportunity discovery and ranking engine.

Expand:
- permitted APIs/feeds/connectors
- employer career pages
- global normalization
- cross-source deduplication
- source reliability
- global role taxonomy
- capability clustering
- global remote intelligence
- global salary/location analysis
- recruiter intelligence
- company intelligence
- global opportunity scoring
- source analytics
- global ranking

Initial source families include India, Middle East, Australia, New Zealand and global remote sources, subject to access conditions.

## 7. v0.3 — Global Mobility

### Objective

Add career-to-country decision intelligence.

### Country sequence

1. Australia
2. New Zealand
3. UAE
4. Qatar
5. Saudi Arabia
6. Singapore
7. UK
8. Canada
9. Germany/EU

### Modules

- country profiles
- occupation mapping
- skills assessment
- sponsorship intelligence
- visa pathway data
- salary thresholds
- qualification requirements
- language requirements
- points/rules where applicable
- state/regional pathways
- relocation feasibility
- employer sponsorship
- job-to-occupation compatibility
- versioned official rules
- verification dates
- legal-information disclaimer

### Global Opportunity Score

```text
Career Fit
+
Job Fit
+
Company Fit
+
Remote Fit
+
Salary Fit
+
Mobility/Visa Fit
+
Sponsorship Fit
+
Relocation Fit
```

## 8. v1/v2 — SaaS Platform

### Objective

Productize the proven system.

Modules:
- subscriptions
- entitlements
- usage limits
- billing
- AI cost governance
- multi-user administration
- advanced audit/security
- advanced automation
- recruiter features
- career coach features
- B2B capabilities
- partner integrations
- broader global coverage
- production-scale observability
- data governance

Indicative plans:
- Free
- Pro
- Global
- Executive

Payment integration may be deferred until commercialization.

## 9. Dependency Principles

1. Career Vault precedes serious personalization.
2. Career Ontology and Job DNA precede advanced semantic matching.
3. Truth & Compliance precedes trusted application generation.
4. Application CRM precedes meaningful outcome learning.
5. Company Intelligence feeds both Application and Interview layers.
6. Interview Intelligence precedes Live Interview Assistant.
7. Global Job Intelligence expands discovery before Global Mobility expands country decisions.
8. SaaS commercialization comes after v0.1 usefulness is proven.

## 10. Shared Architecture Across Versions

The following should remain stable unless a material architectural decision is documented:

```text
Career Vault
Persona abstraction
Job model
Job DNA
Evidence/provenance
Application lifecycle
AI provider abstraction
Tenant/security boundary
API/service separation
PostgreSQL/pgvector direction
Frontend/backend contract
Auditability
```

New versions add capabilities around these foundations rather than creating parallel systems.

## 11. Final End-State Module Map

```text
CareerOS
|
+-- Identity & Tenant
|
+-- Career Intelligence
|    +-- Career Vault
|    +-- Evidence Graph
|    +-- Career Ontology
|    +-- Career Strategy
|
+-- Persona Engine
|
+-- Job Intelligence
|    +-- Discovery
|    +-- Job Inbox
|    +-- JD Analyzer
|    +-- Job DNA
|    +-- Connectors
|    +-- Deduplication
|    +-- Source Intelligence
|
+-- Matching Engine
|    +-- Eligibility
|    +-- Mandatory Requirements
|    +-- Semantic Matching
|    +-- Evidence Matching
|    +-- Opportunity Scoring
|    +-- Explanations
|
+-- Intelligence
|    +-- Remote Intelligence
|    +-- Company Intelligence
|    +-- Recruiter Intelligence
|    +-- Global Mobility
|    +-- Migration Intelligence
|
+-- Application Factory
|    +-- Resume Studio
|    +-- Cover Letter
|    +-- Application Answers
|    +-- Recruiter Messaging
|    +-- Truth & Compliance
|    +-- Approval
|
+-- Career CRM
|    +-- Applications
|    +-- Recruiters
|    +-- Interviews
|    +-- Offers
|    +-- Outcomes
|
+-- Interview Intelligence
|    +-- Preparation
|    +-- Mock Interview
|    +-- Question Prediction
|    +-- Live Interview Assistant
|    +-- Outcome Learning
|
+-- Analytics
|
+-- Web GUI
|
+-- AI Orchestration
|
+-- SaaS
|    +-- Billing
|    +-- Entitlements
|    +-- Usage
|    +-- B2B
|
+-- Security / Governance
```

## 12. Version Completion Philosophy

A version is complete when its intended user outcome works end-to-end.

A version is not complete merely because its modules exist as folders, routes, models or stubs.

## 13. Long-Term Invariant

CareerOS remains career-centric, not job-title-centric.

The Career Vault remains the factual source of truth.

Jobs become structured Job DNA.

Matching is capability/evidence-driven.

Applications preserve the employer's advertised title.

Generated career claims are evidence-backed.

Global mobility is a decision layer, not merely a visa database.
