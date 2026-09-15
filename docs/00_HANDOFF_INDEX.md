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

- **Global Intelligence Engine / AI Orchestration** — one provider-neutral gateway and routing layer for all AI workloads
- Truth & Compliance
- Skill Gap Intelligence
- Remote Intelligence
- Company Intelligence
- Web GUI
- Security / Governance
- Analytics / Learning
- Source/Connector Layer

The Global Intelligence Engine is platform-wide and multi-user. Individual modules must not call AI vendors directly. Provider credentials are platform configuration, stored encrypted at rest, and managed by authorized developer/admin users from Project Control.

## 6. Current architecture decision — CV intelligence

The current M02 Professional Profile workflow is **AI-first for CV understanding**:

```text
CV Upload
→ PDF/document text extraction
→ Global Intelligence Engine
→ AI semantic CV understanding
→ structured candidate facts
→ CareerOS validation/reconciliation/provenance/trust policy
→ Professional Profile / Career Vault
```

Deterministic parsing remains supporting infrastructure for preprocessing, validation, normalization, source verification and safety. It must not replace the current AI-first CV-understanding workflow or make the workflow dependent on exact CV headings/regex structure.

Personas are generated later from the completed profile/Career Vault; they are not generated during CV ingestion.

The authoritative evolution and runtime decision record is:

`docs/AI_TAKEOVER/07_ARCHITECTURE_EVOLUTION_AND_GLOBAL_INTELLIGENCE_RUNTIME.md`

## 7. Global Intelligence runtime controls

The Global Intelligence Engine is an operational runtime, not merely a provider settings page. The four Project Control areas are real runtime capabilities:

1. **Task-based routing** — deterministic routing by task, capability, provider health, priority, cost policy, quota and data classification.
2. **Fallback routing** — ordered, policy-controlled fallback with every provider attempt recorded and the actual provider surfaced.
3. **Usage & cost controls** — request attribution, request limits, token usage when reported, and cost only when reliably calculable; never fabricate usage/cost.
4. **Health / latency / quota** — provider health, failures, fallback counts, latency and provider quota/rate-limit information where available, with explicit no-data states.

All workloads pass through:

```text
CareerOS feature
→ Global Intelligence Runtime
→ deterministic task router
→ gateway/provider adapter
→ approved provider
```

AI is not the system of record. CareerOS application services remain authoritative for persistence and application state. An empty AI section is never permission to delete existing facts.

## 8. Version map

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

## 9. Delivery rule

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

## 10. AI roles

### ChatGPT
Lead Architect, QA, reviewer, security reviewer, release/verification gate.

### DeepSeek
Developer, coder, implementation engineer.

The roles are complementary; neither should silently assume the other's authority.
