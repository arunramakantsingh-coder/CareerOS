# CareerOS — AI TAKEOVER ENTRYPOINT

**This file is intentionally at repository root so an AI given only the GitHub repository URL has an immediate handover path.**

CareerOS is an existing **AI-powered Global Career Operating System**. Do not rebuild it. GitHub is the implementation source of truth; actual local runtime evidence is the verification source of truth.

## FIRST ACTION

Read this file, then inspect the exact current branch and commit. The active v0.2 development line at the 2026-09-03 handover is:

`working/m02-profile-builder-v1.3-20260902` @ `a3dc548`

The complete current handover is maintained on that branch under:

`docs/AI_TAKEOVER/`

Start with:

1. `docs/AI_TAKEOVER/01_PROJECT_REQUIREMENTS_BASELINE.md`
2. `docs/AI_TAKEOVER/02_CURRENT_STATE_20260903.md`
3. `docs/AI_TAKEOVER/03_GIT_BRANCH_AND_RELEASE_CONTROL.md`
4. `docs/AI_TAKEOVER/04_SESSION_HANDOVER_TEMPLATE.md`
5. `docs/AI_TAKEOVER/05_LIVE_HANDOVER.md`
6. `docs/21_AI_TO_AI_COORDINATION_PROTOCOL.md`
7. `docs/22_CAREEROS_CURRENT_CONTROL_STATE.md`
8. `docs/23_CAREEROS_MODULE_VERSION_REGISTRY.md`

## CURRENT PRODUCT PRIORITY

Profile first:

`Profile Builder → CV + Professional Document Vault → Profile Intelligence → Personas → Global Job Discovery → Email Intelligence → Company/Recruiter Intelligence → Job Intelligence/Matching → Skill Gap → Application Factory/CRM → Live Interview Assistant → Analytics/Learning → Global Mobility`

v0.1 Personal Job & Interview Copilot is frozen. v0.2 Global Job Intelligence is the current release line.

## CRITICAL BRANCH WARNING

`working/live-interview-workspace-v0.2.2-20260902` is a diverged older working line, not the current continuation. At handover it was 16 commits behind and 1 commit ahead of the current profile branch, with merge base `9bd4d80`. Reconcile it before integration; never select it merely because its version number is higher.

## PRODUCT REQUIREMENTS TO PRESERVE

- Google SSO/OIDC and LinkedIn SSO/OIDC are required; Gmail mailbox authorization is a separate Google permission.
- Profile Builder is a complete editable job-portal-grade professional profile: personal details, CV, headline, summary, skills/IT skills, employment 1..N, education 1..N, certifications, projects, accomplishments, career profile and Profile Performance.
- CV intake remains independently available from the Professional Document Vault.
- Professional Document Vault supports multiple files, drag/drop, folders, ZIP, camera/scan where browser/device security permits, parsing/OCR, classification, metadata/indexing and provenance.
- Evidence flows into Profile Intelligence and suggests canonical profile data without silently overwriting user-confirmed values.
- Vertical navigation is domain-level: Overview, Professional Identity, Opportunity, Interview & Insight, Global, Project Control.
- Horizontal navigation is contextual sub-navigation and must not duplicate the vertical domain list.
- Profile identity stays visible in the top shell.
- Application settings are global application settings, not profile settings.
- Forms must preserve text-input focus, use compact calendar date pickers, and use controlled dropdowns for enumerated values such as seniority.
- Project control must maintain Bug Tracker, Project Tracker, Roadmap, Module/Version Registry and AI handover state.
- Live Interview is intended as real-time, permission-aware assistance, not interview preparation; its answer panel must be concise, indicative and evidence-grounded.

## NON-NEGOTIABLES

Inspect before changing. Reuse before creating. Patch before replacing. Preserve working functionality. Never modify an applied Alembic migration. Never commit secrets. Never fabricate career/job/company/immigration facts. Never claim tests or VERIFIED status without actual evidence. Use versioned branches and backups. Record blockers instead of hiding them.

## HANDOVER RULE

Every AI session must leave the exact branch, commit, milestone, changes, tests, runtime evidence, bugs, blockers, decisions, unfinished work and next action in `docs/AI_TAKEOVER/05_LIVE_HANDOVER.md`.

If only the default branch is visible, inspect the branch list and move to the branch named by the current handover record before changing code.
