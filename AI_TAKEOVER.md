# CareerOS — AI TAKEOVER / FIRST-READ

**Purpose:** This file is the first-read handover for any AI agent taking over CareerOS. It is deliberately short enough to be loaded before the deeper control-plane documents.

## 1. Product

CareerOS is an **AI-powered Global Career Operating System**. It builds a canonical professional identity from user-entered information and evidence, discovers global opportunities, converts jobs into structured Job DNA, matches capability/evidence, supports truthful applications and interview intelligence, and learns from outcomes.

CareerOS is **not** merely a job board, static CV builder, title-search engine, or blind auto-apply bot.

## 2. Current product priority

**PROFILE FIRST.** The current work is the M02 Profile Builder / Professional Identity foundation. Do not jump to Global Job Discovery or Live Interview implementation until the profile/evidence foundation is accepted.

Current intended sequence:

```text
Foundation
→ Authentication / Identity
→ Profile Builder
→ CV + Professional Document Vault
→ Profile Intelligence / Evidence Reconciliation
→ Personas
→ Global Job Discovery
→ Email Intelligence
→ Company / Recruiter Intelligence
→ Job Intelligence + Matching
→ Skill Gap Intelligence
→ Application Factory + CRM
→ Live Interview Assistant
→ Analytics / Learning
→ Global Mobility
→ Advanced automation / SaaS
```

## 3. Current Git truth (2026-09-05)

The repository is `arunramakantsingh-coder/CareerOS`.

Important refs currently present:

- `release/v0.1-personal-job-interview-copilot` — frozen v0.1 release line.
- `release/v0.2-global-job-intelligence` — v0.2 release baseline at `1da1670`.
- `working/m02-professional-identity-v1.6-reconciled-20260905` — current M02 continuation under development; PR #19 targets the v0.2 release baseline.
- `working/m02-profile-builder-v1.3-20260902` — historical profile-builder working line; do not assume it is current merely because older documentation names it.
- `working/live-interview-workspace-v0.2.2-20260902` — **diverged/legacy live-interview work line**; it must NOT be treated as the current product baseline without reconciliation.
- `backup/pre-ai-handover-20260903` — historical safety checkpoint before the original control-plane documentation work.

Current M02 integration rule:

```text
v0.2 release baseline
        ↓
M02 v1.6 reconciled branch
        ↓
local Docker + browser acceptance
        ↓
M02 audit / QA
        ↓
release integration only after approval
```

Do not merge PR #19 automatically. Runtime acceptance is the current gate.

## 4. Source-of-truth hierarchy

```text
GitHub implementation
        ↓
Local runtime evidence
        ↓
Approved project/control-plane docs
        ↓
Conversation/history as requirements context
        ↓
Old ZIPs, screenshots and stale assessments
```

GitHub is canonical implementation truth. A local browser observation is runtime/acceptance evidence. Old ZIPs and temporary copies are not authoritative.

## 5. AI roles

### Human / Product Owner — Arun
Owns product intent, local execution, secrets/provider setup, browser/UI acceptance and runtime evidence.

### ChatGPT
**Lead Architect / Product Architect / Application Architect / QA Lead / Security Reviewer / Release & Verification Gate.** Owns architecture direction, acceptance criteria, regression protection, evidence review and authorization of milestone progression.

### Coding AI / Implementation Engineer
The coding AI works directly against the authorized GitHub development branch when repository write access is available. It implements approved work, creates tests, performs code-level validation, reports exact changes and stops at the defined milestone boundary. It must never self-declare final verification.

Any other AI is a temporary contributor and must first read this file plus `AGENTS.md` and the relevant control-plane documents.

## 6. Non-negotiable engineering rules

1. Inspect before changing; reuse before creating; patch before replacing.
2. Never rebuild the application from scratch.
3. Preserve working features and previous verified behavior.
4. Never modify an applied Alembic migration; add a new migration.
5. Never commit secrets, `.env` values, OAuth client secrets or tokens.
6. Never fabricate career, job, company, certification, experience or immigration facts.
7. Never claim `VERIFIED` without executable evidence and reviewer approval.
8. Never trust client-supplied tenant identity; enforce ownership from authenticated identity.
9. Keep CV intake separate from the Professional Document Vault, while allowing both to enrich the canonical profile.
10. Keep application settings separate from career/profile data.
11. Do not silently change version boundaries or product scope.
12. Do not mix unrelated cleanup with a milestone.
13. Every material change must be documented in Git and the control plane.

## 7. Product requirements that must survive handover

### Authentication and external identity
- Email/password authentication remains supported.
- Google SSO/OIDC is required.
- LinkedIn SSO/OIDC is required.
- LinkedIn profile synchronization is required where the approved LinkedIn API permissions permit it.
- Google sign-in and Gmail mailbox authorization are **different grants**. Gmail requires explicit additional authorization for mailbox access.
- OAuth provider credentials and exact callback registration are external configuration and must never be invented by code.

### Professional Identity / Profile Builder
The user logs in and lands on the dashboard. Profile is the career record the user can inspect, edit and complete.

The profile must support a job-portal-grade single profile experience covering, at minimum:

- Personal details
- Resume / CV
- Resume headline
- Profile summary
- Key skills
- IT skills
- Employment / Work Experience 1..N
- Education 1..N
- Certifications
- Projects
- Accomplishments
- Career profile / targeting preferences
- Profile Performance / completeness
- Missing-information prompts
- Editable user-confirmed values
- Evidence/provenance indicators for automatically populated values

Documents may suggest profile facts, but user-confirmed information must not be silently overwritten.

### CV intake vs Professional Document Vault
These are separate user capabilities:

**CV intake:** dedicated CV upload/replace/use-as-resume flow.

**Professional Document Vault:** multiple files, drag-and-drop, folder selection, ZIP ingestion, camera/scan capture where the browser permits it, parsing/OCR, classification, metadata/indexing, provenance and evidence extraction.

The vault is the evidence store; extracted information should enrich Profile Intelligence and then the editable Profile Builder.

### Evidence pipeline

```text
CV / document / scan
→ safe ingestion
→ file metadata + hash
→ parsing / OCR
→ classification
→ extraction + confidence
→ provenance / source reference
→ reconciliation
→ canonical profile suggestion
→ user confirmation/edit
```

The metadata/indexing layer is important because future profile fields, job matching and AI reasoning need traceable source evidence.

### Navigation / shell
Vertical navigation is **domain-level** and must not duplicate the horizontal navigation.

Vertical domains:

- Overview
- Professional Identity
- Opportunity
- Interview & Insight
- Global
- Project Control

The horizontal bar is contextual to the selected domain. Under Professional Identity it can expose Profile, Profile Setup, Profile Intelligence, CV & Documents / Document Vault, Career Vault and Personas. Other domains receive their own contextual sub-navigation.

Profile identity should remain visible in the top shell across pages. The UI should feel like a professional career operating system: translucent/dimensional, technically sophisticated, readable and calm — not a flat black web page and not a duplicated menu.

### Application Settings
Settings are **application-wide settings**, not profile settings. Appearance, account/session, integrations/connections, privacy/evidence and system health belong here. Settings should use vertical internal browsing where appropriate.

### Global form UX
- Text inputs must preserve focus and accept complete strings; never implement a state/update pattern that causes one-character-at-a-time entry.
- Date fields should use a small calendar/date-picker allowing month/year navigation and date selection.
- Enumerated fields should use explicit dropdowns. Example seniority values: Entry-Level, Mid-Level, Senior-Level, Lead / Principal, Executive / C-Suite.
- Every feature must have loading, empty, error and validation states.

### Project control
CareerOS must keep these visible and maintained:

- Bug Tracker
- Project Tracker
- Roadmap
- Module / Version Registry
- AI-to-AI coordination and current control state

These are engineering control surfaces, not decorative pages.

### Live Interview Assistant
This is **real-time interview assistance**, not interview preparation. The intended future workspace can receive permitted live transcription/context from supported meeting/audio integrations and produce extremely concise, indicative answer cues.

Preferred answer style:

```text
Weight: Highest wins — Cisco local
Local Preference: Highest wins — AS-wide
AS Path: Shortest wins
Origin: IGP > EGP > Incomplete
MED: Lowest wins
```

Do not turn the answer panel into paragraphs or essays. Keep evidence/context available without overwhelming the user. Existing documentation requires permission-aware use when the interviewer/assessment explicitly allows AI assistance.

## 8. Current known risks / unresolved areas

At handover time, do not mark these verified merely because routes/files exist:

- Google/LinkedIn provider credentials and provider-side callback registration still require real configuration/runtime evidence.
- Gmail mailbox authorization requires separate Google consent/scopes.
- The live-interview working branch is stale/diverged from the current profile branch and must be reconciled before being treated as the next integrated release.
- Profile/Vault/CV flows require local runtime QA, not code-only approval.
- Historical bug records include OAuth configuration feedback still under review and other profile/vault fixes that require retesting.
- Existing docs contain some stale branch/status wording; when a conflict is found, prefer actual Git refs + runtime evidence and record the discrepancy rather than silently rewriting history.

## 9. Mandatory takeover procedure

When an AI takes over:

```text
1. Read AI_TAKEOVER.md
2. Read AGENTS.md
3. Read docs/21_AI_TO_AI_COORDINATION_PROTOCOL.md
4. Read docs/22_CAREEROS_CURRENT_CONTROL_STATE.md
5. Read docs/23_CAREEROS_MODULE_VERSION_REGISTRY.md
6. Read the relevant product/domain docs
7. Inspect Git branches + current commit + working tree
8. Compare the intended milestone against actual code
9. Check BUG_TRACKER.md and PROJECT_TRACKER.md
10. State: UNDERSTOOD / BLOCKED / READY
11. Work only on the authorized milestone
12. Record implementation, tests, evidence, blockers and next action
13. Update the handover/control documents before stopping
```

## 10. Mandatory AI-led development / execution workflow

**This is the normal CareerOS development process.** The human and lead AI discuss and agree what should be built or fixed; the coding AI then implements directly in the authorized GitHub development branch when write access is available. The human should not be used as a manual source-file editor for normal development.

```text
USER + LEAD AI
    ↓
Discuss requirement / bug / module phase
    ↓
Define exact acceptance criteria + scope
    ↓
LEAD AI authorizes implementation
    ↓
CODING AI / IMPLEMENTATION AGENT
    ↓
Inspect GitHub branch, ancestry, code, migrations, tests
    ↓
Implement directly on authorized GitHub working branch
    ↓
Add/update tests + migration(s) where required
    ↓
Run available code-level validation / CI
    ↓
Commit changes + document exact implementation state
    ↓
LEAD AI reviews GitHub diff / tests / architecture
    ↓
If acceptable: hand user the local verification procedure
    ↓
USER pulls exact branch + rebuilds local Docker/runtime
    ↓
USER executes browser/API/database acceptance checks
    ↓
USER reports observed evidence
    ↓
LEAD AI diagnoses failures using GitHub + local evidence
    ↓
CODING AI fixes if required
    ↓
Repeat until acceptance criteria are met
    ↓
LEAD AI performs final QA/release review
    ↓
Only then may the milestone be marked VERIFIED / integrated
```

### Human local-testing handoff standard

After completing a GitHub implementation, the coding/lead AI must **not** simply say “please test locally.” It must provide a reproducible local verification package containing:

1. Exact branch to pull.
2. Exact commit SHA to expect, when relevant.
3. Exact project-root path assumption or a command to reach it.
4. Exact `git pull` / checkout commands.
5. Exact Docker rebuild/start commands.
6. Exact migration/database commands when schema changes exist.
7. Exact health/API/browser routes to test.
8. Exact expected results.
9. Exact negative/regression checks for the changed area.
10. A warning for destructive commands that must **not** be run.
11. What output/screenshots/logs the human should return if something fails.

For database changes, never instruct the user to delete the PostgreSQL volume merely to make a migration pass. Preserve data unless the task explicitly authorizes destructive reset.

### Implementation reporting standard

Every completed coding task must report:

```text
Implementation status
Branch
Commit SHA
Scope / objective
Files changed
Database / migrations
API changes
UI changes
Tests actually executed
CI status actually observed
Known limitations
Local verification commands
Expected results
What remains unverified
```

The report must distinguish:

```text
IMPLEMENTED ≠ TESTED ≠ OBSERVED ≠ REVIEWED ≠ VERIFIED
```

### Git safety gates

- Never code directly on a release branch unless the control plane explicitly authorizes it.
- Never merge a PR automatically merely because it is mergeable.
- Never force-push or rewrite another agent's work without explicit authorization.
- Before material changes, inspect branch, HEAD, ancestry and working state.
- Keep unrelated changes out of milestone commits.
- Prefer a new working branch for a new material implementation phase.
- Preserve a recovery point before risky migrations or large reconciliations.

## 11. Required handover update

Before an AI stops work, it must update the current-state record with:

```text
Timestamp
Active branch
Commit SHA
Milestone / module
Objective
What changed
Files changed
DB/migrations
APIs
UI
Tests actually run
Runtime evidence
Known bugs
Blockers
Decisions / ADRs
What is NOT complete
Exact next action
```

If the AI is stuck, **the blocker is part of the deliverable**. Never hide it.

## 12. Short takeover prompt for a new AI

Copy/paste this into a new coding-AI session:

> **CAREEROS AI TAKEOVER — START HERE**
>
> You are taking over an existing production-oriented CareerOS repository. Do not rebuild it and do not assume the previous AI's status is correct. Repository: `arunramakantsingh-coder/CareerOS`.
>
> First read: `AI_TAKEOVER.md`, `AGENTS.md`, `docs/AI_TAKEOVER/05_LIVE_HANDOVER.md`, `docs/21_AI_TO_AI_COORDINATION_PROTOCOL.md`, `docs/22_CAREEROS_CURRENT_CONTROL_STATE.md`, `docs/23_CAREEROS_MODULE_VERSION_REGISTRY.md`, then the relevant product/spec documents.
>
> Then inspect the **actual GitHub state**: branches, current authorized branch, HEAD SHA, ancestry, PRs, changed files, migrations, tests and CI. Reconcile documentation against GitHub instead of trusting stale branch names or chat history.
>
> State your takeover result as **UNDERSTOOD / BLOCKED / READY**, identify the single authorized milestone, and name the exact next action.
>
> Development model: discuss/define the work with the lead AI first; then implement directly in the authorized GitHub working branch when write access is available. Inspect before changing. Preserve working functionality. Make small reversible changes. Never modify applied migrations; add new migrations. Add regression tests. Never commit secrets. Do not touch v0.1 or unrelated modules. Do not merge release PRs without approval.
>
> When implementation is complete, report the exact branch/commit, files, migrations, APIs/UI, tests and CI status. Then provide the human with exact local pull/rebuild/migration/test commands and expected results. Wait for local runtime evidence. Do not call the feature VERIFIED until runtime evidence and QA/release approval exist.
>
> Before ending the session, update the live handover/current-state records so the next AI can continue from GitHub alone.

## 13. Required handover update

Before an AI stops work, it must update the current-state record with:

```text
Timestamp
Active branch
Commit SHA
Milestone / module
Objective
What changed
Files changed
DB/migrations
APIs
UI
Tests actually run
Runtime evidence
Known bugs
Blockers
Decisions / ADRs
What is NOT complete
Exact next action
```

If the AI is stuck, **the blocker is part of the deliverable**. Never hide it.
