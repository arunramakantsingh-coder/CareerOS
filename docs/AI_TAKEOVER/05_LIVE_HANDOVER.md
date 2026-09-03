# CareerOS — LIVE HANDOVER SNAPSHOT

> Update this file at the end of every material AI session. The goal is that a new AI can continue without access to prior chat.

## Snapshot

- Date: 2026-09-03
- Current development line: `working/m02-profile-builder-v1.3-20260902`
- Current implementation HEAD at snapshot start: `a3dc54842961362b708b8849ac2e7ec79feab4f0`
- Safety checkpoint: `backup/pre-ai-handover-20260903`
- Active product release: v0.2 Global Job Intelligence
- Active milestone: M02 Profile Builder / Professional Identity reconciliation
- Overall status: **IMPLEMENTATION PRESENT / RUNTIME & E2E ACCEPTANCE PENDING**

## What the current branch represents

The profile branch is materially ahead of the v0.2 release baseline and contains the current reconciliation work for authentication, document ingestion, profile intelligence, profile UI, unified shell/navigation, project control pages and related fixes.

## Current top-priority validation areas

1. Profile Builder CRUD and complete profile sections.
2. CV intake remains separate from Professional Document Vault.
3. Multi-file/folder/ZIP/camera document intake and extraction.
4. Evidence/provenance linkage from documents into profile suggestions.
5. Google SSO runtime with real provider credentials.
6. Separate Gmail authorization runtime.
7. LinkedIn SSO/profile sync runtime with actual provider permissions.
8. Text-input focus regression: typing a full string must not lose focus after one character.
9. Date-picker and controlled dropdown behavior.
10. Vertical domain navigation vs contextual horizontal navigation.
11. Application-wide settings separation.
12. Bug Tracker / Project Tracker / Roadmap accuracy.

## Known branch issue

`working/live-interview-workspace-v0.2.2-20260902` is not the current continuation. It diverges from the profile branch and is 16 commits behind / 1 ahead with merge base `9bd4d80`. The live interview page must be reconciled onto the current profile line before integration.

## Known documentation issue

`docs/PROJECT_TRACKER.md` currently names `working/m02-profile-repair-v1.2-20260902` as its current working branch even though the current profile branch is `working/m02-profile-builder-v1.3-20260902`. This is documentation drift and must be corrected as part of project-control maintenance.

## External prerequisites

OAuth cannot be completed by source code alone. Google and LinkedIn provider applications must have valid client credentials and exact local callback registrations. Gmail mailbox access requires a separate Google authorization grant. No secrets belong in Git.

## Verification rule

No feature is `VERIFIED` until actual runtime evidence, relevant tests, regression checks and QA review are recorded.

## Next AI action

Start with repository/branch reconciliation and inspect the current profile branch. Do not switch to the old live-interview branch. Complete M02 profile/evidence QA and documentation reconciliation first. Then prepare a separate controlled reconciliation milestone for Live Interview, followed by Opportunity / Global Job Discovery.
