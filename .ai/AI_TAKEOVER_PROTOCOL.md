# CareerOS — UNIVERSAL AI TAKEOVER PROTOCOL

## Mission

You are taking over an existing CareerOS repository. Your first responsibility is continuity, not coding.

Do not assume the previous AI was correct. Do not assume it was wrong. Reconstruct the current state from Git, code, control-plane records and runtime evidence.

## TAKEOVER PROCEDURE

### Step 1 — Identify the repository

Read `AI_TAKEOVER.md` and identify the active branch and commit.

### Step 2 — Inspect lineage

Check:
- current branch
- HEAD SHA
- parent/ancestry
- backup branches
- release branches
- working branches
- divergent feature branches
- recent PRs/commits

Never switch branches just because a branch name contains a higher version number.

### Step 3 — Read the control plane

Read:
- `.ai/README.md`
- `.ai/ROLE_MATRIX.md`
- this protocol
- `docs/AI_TAKEOVER/*`
- coordination protocol
- current control state
- module/version registry

### Step 4 — Reconcile documentation

Compare documentation claims with actual Git state. If stale, record the drift before changing implementation.

### Step 5 — Inspect the requested module

Search for existing routes, components, models, schemas, services, migrations, tests and usages before creating anything.

### Step 6 — Establish a change boundary

Write down:
- objective
- authorized milestone
- files/modules likely affected
- non-goals
- regression risks
- database/API impact

### Step 7 — Protect working functionality

Do not rewrite shared components wholesale. Do not alter authentication, migrations or unrelated pages unless investigation proves it necessary.

### Step 8 — Implement incrementally

Use a focused working branch. Make small changes. Keep commits meaningful and reversible.

### Step 9 — Verify

Run the smallest relevant checks first, then integration/runtime checks. Never report a test as passed unless it was actually executed.

### Step 10 — Record evidence

Update the module registry and live handover. Include exact commands/results where useful.

### Step 11 — Integrate

Use a PR into the authorized continuation branch. Do not merge automatically unless the owner has explicitly authorized it.

## PRODUCT RULES

CareerOS is evidence-first. The professional evidence layer supports the canonical career profile.

CV intake is independently available from the Professional Document Vault.

Professional Document Vault supports multiple files, drag/drop, folders, ZIP, camera/scan where permitted, extraction/OCR, classification, metadata, indexing, duplicate/version handling and provenance.

Profile Builder is editable and job-portal-grade: personal details, resume, headline, summary, skills/IT skills, employment 1..N, education 1..N, certifications, projects, accomplishments, career profile and performance/completeness.

Extracted data is derived until accepted. Never silently overwrite user-confirmed facts. Conflicts require explicit review.

Google SSO and LinkedIn SSO are identity integrations. Gmail mailbox authorization is a separate Google permission. External provider credentials and redirect registrations are never stored in Git.

Live Interview Assistant is a real-time, permission-aware assistance workspace, not interview preparation. Keep its answer cues short, indicative and evidence-grounded.

## UI CONTRACT

Vertical domains:
- Overview
- Professional Identity
- Opportunity
- Interview & Insight
- Global
- Project Control

Horizontal navigation is contextual sub-navigation for the selected vertical domain. Never duplicate the vertical list horizontally.

Persistent shell:
- profile identity visible at top
- Home/Dashboard reachable
- overflow/menu for additional application controls
- application settings are global
- theme is global and persistent

Themes:
- Light: professional workspace
- Dark: premium AI workspace
- Techno: translucent futuristic operating-system/command-center aesthetic, not a gaming UI

## DATA / SECURITY CONTRACT

- User-owned data must be tenant scoped and authorized.
- Never trust client-supplied tenant identifiers.
- Never commit secrets or credentials.
- Preserve original evidence.
- Store derived OCR/extraction separately.
- Record source, page where possible, confidence, method and timestamp.
- ZIP extraction must defend against path traversal, decompression/size abuse and dangerous file types.
- Do not expose employer-confidential/project material unnecessarily.

## SESSION CLOSEOUT TEMPLATE

At the end of a material session, update `docs/AI_TAKEOVER/05_LIVE_HANDOVER.md` with:

```text
Date/time:
Active branch:
HEAD SHA:
Backup checkpoint:
Release:
Milestone:
Module/version:
Objective:
Implemented:
Changed files:
Created files:
Tests executed:
Runtime evidence:
Known bugs:
Blockers:
Decisions:
Risks:
Deferred:
Exact next action:
Status:
```

## HANDOVER PROMPT

If a human gives another AI only the repository URL, the human can say:

> Take over CareerOS. Read `AI_TAKEOVER.md` first, then the `.ai` control plane and `docs/AI_TAKEOVER`. Reconstruct the current Git lineage and runtime state. Do not code until you understand the active branch, milestone, module registry, known bugs, blockers and exact next action. Preserve existing functionality and use the smallest reversible change. Update the handover before you stop.
