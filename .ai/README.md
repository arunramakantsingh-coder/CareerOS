# CareerOS — AI CONTROL PLANE

This directory is the persistent, AI-readable control plane for CareerOS.

## Purpose

Any AI agent taking over this repository must be able to reconstruct the project without access to a previous chat session.

Git is the implementation history. The control plane is the continuity layer. Runtime evidence is the truth for whether a feature actually works.

## First read

1. `/AI_TAKEOVER.md`
2. `/AGENTS.md`
3. `/.ai/AI_TAKEOVER_PROTOCOL.md`
4. `/.ai/ROLE_MATRIX.md`
5. `/docs/AI_TAKEOVER/01_PROJECT_REQUIREMENTS_BASELINE.md`
6. `/docs/AI_TAKEOVER/02_CURRENT_STATE_20260903.md`
7. `/docs/AI_TAKEOVER/03_GIT_BRANCH_AND_RELEASE_CONTROL.md`
8. `/docs/AI_TAKEOVER/05_LIVE_HANDOVER.md`
9. `/docs/21_AI_TO_AI_COORDINATION_PROTOCOL.md`
10. `/docs/22_CAREEROS_CURRENT_CONTROL_STATE.md`
11. `/docs/23_CAREEROS_MODULE_VERSION_REGISTRY.md`

Then inspect the actual Git branch, commit, diff, tests and runtime before making changes.

## Source-of-truth hierarchy

1. Actual source code + Git history
2. Actual runtime/test evidence
3. Current control-plane/handover records
4. Product requirements/specification
5. Historical conversation context

If these disagree, do not silently choose. Reconcile and record the discrepancy.

## Current product order

Identity → Profile Builder → CV + Professional Document Vault → Profile Intelligence → Personas → Opportunity/Global Job Discovery → Email Intelligence → Company/Recruiter Intelligence → Job Intelligence/Matching → Skill Gap → Application Factory/CRM → Live Interview Assistant → Analytics/Learning → Global Mobility.

## Permanent rule

Every material AI session must leave a current handover record containing: branch, commit, objective, completed work, changed files, tests, runtime evidence, defects, blockers, decisions, risks, and exact next action.
