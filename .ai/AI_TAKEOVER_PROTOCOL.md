# CareerOS — UNIVERSAL AI TAKEOVER PROTOCOL

A new AI must establish continuity before coding.

## Mandatory takeover

1. Read `AI_TAKEOVER.md`, `AGENTS.md` and the `.ai` directory.
2. Read `docs/AI_TAKEOVER/` plus the coordination protocol, current control state and module/version registry.
3. Inspect actual branches, HEAD, ancestry, backups, recent commits and PRs.
4. Identify the authorized active development line; never choose by version number alone.
5. Inspect the requested implementation and all usages before changing it.
6. State objective, milestone, module, non-goals, affected files, DB/API impact and regression risks.
7. Make the smallest reversible change in a focused versioned branch.
8. Run relevant tests/build/runtime checks.
9. Record actual evidence and update the live handover.
10. Integrate only through the authorized PR workflow.

## Product continuity

CareerOS is an AI-powered Global Career Operating System and an existing codebase. The current v0.2 order is:

Identity → Profile Builder → CV + Professional Document Vault → Profile Intelligence → Personas → Global Job Discovery → Email Intelligence → Company/Recruiter Intelligence → Job Intelligence/Matching → Skill Gap → Application Factory/CRM → Live Interview Assistant → Analytics/Learning → Global Mobility.

Profile Builder is comprehensive and editable. Document Vault is evidence storage/intelligence. CV intake remains independently available. Evidence-derived facts require provenance and must not silently overwrite user-confirmed facts.

Google SSO and LinkedIn SSO are identity integrations. Gmail mailbox authorization is a separate permission. Provider credentials never belong in Git.

Live Interview Assistant is real-time, permission-aware assistance, not interview preparation; its cues are short and evidence-grounded.

## UI continuity

Vertical domains: Overview, Professional Identity, Opportunity, Interview & Insight, Global, Project Control.

Horizontal navigation is contextual sub-navigation and must not repeat the vertical domains. Profile identity remains visible in the persistent shell. Application settings are global. Light/Dark/Techno are one persistent global theme system. Techno is a translucent futuristic operating-system aesthetic, not a gaming UI.

## Safety

Never modify an applied migration. Never commit secrets. Never fabricate facts. Protect tenant/user authorization. Defend ZIP extraction against traversal and resource abuse. Preserve original evidence. Stop when runtime evidence or branch lineage is insufficient.

## Closeout

Update `docs/AI_TAKEOVER/05_LIVE_HANDOVER.md` with date/time, active branch, HEAD, milestone, module/version, objective, changed files, tests, runtime evidence, bugs, blockers, decisions, risks, deferred work and exact next action.
