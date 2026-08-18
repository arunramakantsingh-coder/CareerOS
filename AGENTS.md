# CareerOS AI Development Rules

## 1. Purpose

CareerOS is an AI-powered Global Career Operating System.

It is an existing codebase. AI agents must extend, repair and evolve the current implementation rather than rebuild the application from scratch.

The documentation set is the project's control plane. Source code is the implementation plane. Every AI or human contributor must keep the two aligned.

## 2. Authoritative Sources and Precedence

Before any architectural or coding change, read:

1. `AGENTS.md`
2. `docs/CAREEROS_SPEC.md`
3. `docs/CAREEROS_BLUEPRINT.md`
4. `docs/CAREEROS_VERSION_ARCHITECTURE.md`
5. `docs/CAREEROS_PROJECT_ASSESSMENT.md`
6. `docs/DEVELOPMENT_ROADMAP.md`
7. `docs/CAREEROS_DEVELOPMENT_WORKFLOW.md`
8. `docs/CAREEROS_PROJECT_STATUS.md`

Source-of-truth precedence:

1. Current repository implementation — authoritative for what currently exists.
2. `AGENTS.md` — mandatory engineering, security and workflow rules.
3. `CAREEROS_SPEC.md` — intended functional requirements.
4. `CAREEROS_BLUEPRINT.md` — intended product/architecture direction.
5. `CAREEROS_VERSION_ARCHITECTURE.md` — canonical version/module allocation and long-term evolution.
6. `CAREEROS_PROJECT_ASSESSMENT.md` — assessed implementation gaps and risks.
7. `DEVELOPMENT_ROADMAP.md` — delivery sequence.
8. `CAREEROS_DEVELOPMENT_WORKFLOW.md` — collaboration procedure.
9. `CAREEROS_PROJECT_STATUS.md` — living current-state record.

When existing implementation differs from intended behavior, do not silently rewrite architecture. Identify the difference, choose the smallest safe change, and document material decisions.

## 3. Product Direction

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

v0.1 must become useful to its first real user before commercialization is prioritized.

## 4. Core Principle

CareerOS is career-centric, not job-title-centric.

Career Vault is the source of truth for factual career information.

Jobs become Job DNA.

Matching occurs at capability, responsibility, evidence and constraint level.

A job can be highly relevant even when its advertised title does not resemble an internal persona title.

## 5. Application Title Rule

The employer's advertised job title is the application title.

Internal personas are matching/positioning constructs.

Example:

```text
Advertised title:
Technology Resilience Lead

Internal matching persona:
Cyber Security Architect

Application title:
Technology Resilience Lead
```

CareerOS may discover a job because its JD matches a persona deeply, but the application must represent the real advertised role.

## 6. Non-Negotiable Engineering Rules

1. Do not rebuild the application from scratch.
2. Inspect existing implementation before changing a subsystem.
3. Prefer the smallest safe, modular change.
4. Preserve working functionality unless a justified change requires otherwise.
5. Do not introduce a new framework without explicit justification.
6. Never modify an already-applied Alembic migration. Create a new migration.
7. Never commit secrets, tokens, passwords, private keys or real credentials.
8. Never trust client-supplied `tenant_id`.
9. Derive tenant context from authenticated identity and enforce ownership.
10. Never fabricate career facts, job facts, company facts or immigration rules.
11. Never claim tests/builds passed unless actually executed.
12. Do not implement unauthorized job scraping or account automation.
13. Keep restricted application submission human-approved.
14. Do not hard-code immigration rules into prompts.
15. Keep AI providers behind replaceable service interfaces.
16. Retrieve only relevant Career Vault evidence for AI calls.
17. Do not keyword-stuff resumes.
18. Every material generated career claim must map to evidence.
19. Mandatory job requirements must be calculated separately from semantic score.
20. A high semantic score must never conceal a hard disqualifier.
21. Do not silently change product scope during implementation.
22. Stop when the requested task is complete; do not perform unrelated cleanup.

## 7. Career Data Integrity

AI may rewrite, summarize, prioritize, reorder and tailor verified information.

AI may not invent employers, dates, technologies, certifications, projects, achievements, metrics, responsibilities, years of experience or immigration facts.

Generated claims must be traceable to Career Vault evidence.

## 8. Job Intelligence Rules

Evaluate advertised title, normalized role family, seniority, responsibilities, capabilities, technologies, architecture domains, leadership, governance, industry, transferable skills, location, employment model, salary, remote restrictions, work authorization, migration/relocation constraints, mandatory requirements and preferred requirements.

Do not perform title-only search.

Prefer permitted APIs, partner feeds, RSS/alerts, permitted integrations and public employer career pages. Respect terms of service, robots rules and automation restrictions.

## 9. Matching Rules

Initial configurable weighting:
- Technical/capability: 25%
- Relevant experience: 20%
- Architecture/domain: 15%
- Leadership/seniority: 10%
- Industry/domain: 10%
- Location/remote: 5%
- Salary: 5%
- Migration/relocation: 5%
- Certification/qualification: 5%

Mandatory failures are a separate decision layer.

## 10. Truth & Compliance

Truth & Compliance is a mandatory gate before an application package becomes `READY_FOR_REVIEW`.

Every material claim must map to Career Vault evidence. Unsupported claims are removed or flagged.

## 11. Security

Protect authentication, tenant isolation, PII, files, provider credentials, logs and audit history.

Required direction includes secure secrets, authorization checks, validation, rate limiting, secure headers/CORS, SSRF protection, prompt-injection defenses, file scanning, PII-safe logging, audit logging and export/deletion controls.

## 12. Migration

Migration information is informational, not legal advice.

Rules must be structured/versioned with country, rule key/value, effective dates, official source and verification date.

Australia and New Zealand are priority markets.

## 13. AI Engineering

Prefer:

```text
Deterministic logic
      ->
Retrieval / embeddings
      ->
Lightweight model
      ->
Stronger model only where justified
```

Use provider abstraction, caching, selective evidence retrieval and AI usage/cost tracking.

## 14. Frontend

Use the existing Next.js/TypeScript/Tailwind direction unless a documented reason requires change.

The Web GUI is a v0.1 deliverable.

Lovable material is design reference, not production source.

## 15. DeepSeek Development Rule

When DeepSeek is used as coding engineer:

1. Read the current GitHub branch/repository first.
2. Read `AGENTS.md`.
3. Read all relevant project MD files, including the version architecture.
4. Inspect existing implementation before changing a subsystem.
5. Follow project rules even when a shortcut appears easier.
6. Do not rely on stale pasted code when current GitHub code exists.
7. Explain conflicts between implementation and intended behavior.
8. Make the smallest reviewable change.
9. Report exact changes and actual tests.

## 16. PowerShell-First Human Execution Rule

For source-code changes, the human should not manually create folders or individual source files.

DeepSeek must produce one complete PowerShell script starting at the project root and handling folder creation, file creation, complete file contents, dependency changes, migrations, relevant tests and validation.

Expected starting location:

```powershell
PS C:\Projects\CareerOS>
```

The script exists to reduce human error, accelerate implementation and make each task reproducible.

## 17. Development Loop

```text
YOU
  |
  v
CHATGPT
  |
  | Task specification
  v
DEEPSEEK
  |
  | Reads current GitHub + MD files
  v
PowerShell implementation script
  |
  | Human runs from project root
  v
Local implementation + tests
  |
  v
GitHub branch / PR
  |
  v
CHATGPT reads actual repository + diff
  |
  +--> APPROVE --> Merge
  |
  +--> CHANGES REQUIRED
          |
          v
       DEEPSEEK fixes
          |
          v
       Tests
          |
          v
       PR review again
```

No milestone is complete merely because an AI agent says it is complete.

## 18. Milestone Review Rule

The human may say:

> `Milestone X is complete; review the repository.`

The reviewer must inspect the actual GitHub branch/PR/current repository and compare implementation against the task, tests and MD files.

## 19. Documentation Rule

The MD files are part of the product control plane.

After every material milestone:
- update `CAREEROS_PROJECT_STATUS.md`
- update `DEVELOPMENT_ROADMAP.md` if sequencing changes
- update `CAREEROS_PROJECT_ASSESSMENT.md` when assessed status changes
- update SPEC/BLUEPRINT/VERSION_ARCHITECTURE when intended product/architecture changes

Never leave a material architectural decision only in chat.

## 20. Safe Upload Rule

GitHub is the canonical repository source whenever the required information exists in GitHub.

Do not upload the whole local project to ChatGPT during normal milestones.

Upload local artifacts only when the required information exists only locally, such as test logs, screenshots, local database/schema evidence with secrets removed, design mockups, private/uncommitted documents or sanitized local configuration.

Never upload `.env` files, passwords, API keys, access tokens, SSH keys, private certificates, credentials, `node_modules`, `.next`, `__pycache__`, `.git`, Git worktrees, caches or unnecessary build output.

## 21. Git Safety

Before major changes inspect `git status` and current branch.

Do not overwrite another developer's uncommitted work.

Do not merge a PR without human approval.

## 22. Completion Standard

A task is complete only when implementation exists, relevant tests/builds actually pass, the app still starts where applicable, no known critical regression remains, GitHub reflects the change, and documentation reflects the new state.
