# CareerOS — Handoff Index & Operating Map

## 1. Product in one sentence

CareerOS is an AI-powered career intelligence platform that continuously understands a candidate's professional identity, discovers opportunities globally, converts JDs into Job DNA, matches capabilities/evidence across multiple personas, explains fit and gaps, supports truthful applications and interviews, and learns from outcomes.

## 2. What CareerOS is not

It is not primarily:

- a generic job board
- a static resume builder
- a job-title keyword search engine
- a blind auto-apply bot

## 3. Foundational product loop

```text
Understand Career
→ Career Passport / Career Vault
→ Personas
→ Discover Jobs
→ Job Extraction
→ JD Intelligence
→ Job DNA
→ Capability/Evidence Matching
→ Eligibility / Hard Failures
→ 60% Skill-Match Highlight
→ Skill Gap Intelligence
→ Opportunity/Remote/Salary/Mobility Fit
→ Resume / Application Factory
→ Truth & Compliance
→ Human Approval
→ Application CRM
→ Company Intelligence
→ Interview Intelligence
→ Outcome
→ Analytics / Learning
→ Improved Career Profile
```

## 4. Seven major engines from the Product Blueprint

1. Career Intelligence Engine
2. Persona Engine
3. Job Intelligence Engine
4. Matching Engine
5. Application Factory
6. Global Mobility Engine
7. Career CRM & Outcome Engine

## 5. Supporting cross-cutting engines

- AI Orchestration
- Truth & Compliance
- Skill Gap Intelligence
- Remote Intelligence
- Company Intelligence
- Web GUI
- Security / Governance
- Analytics / Learning
- Source/Connector Layer

## 6. Version map

```text
v0.1  Personal Job & Interview Copilot
  ↓
v0.2  Global Job Intelligence
  ↓
v0.3  Global Mobility / Migration
  ↓
v1/v2 SaaS
```

Later versions extend the same repository and stable foundations; they do not become separate product architectures.

## 7. Delivery rule

A module is only complete when the required layers are all present:

```text
Database
→ API
→ Domain/AI logic
→ Frontend
→ Executable tests
→ Integration/E2E evidence
→ Review
→ VERIFIED
```

## 8. AI roles

### ChatGPT
Lead Architect, QA, reviewer, security reviewer, release/verification gate.

### DeepSeek
Developer, coder, implementation engineer.

The roles are complementary; neither should silently assume the other's authority.
