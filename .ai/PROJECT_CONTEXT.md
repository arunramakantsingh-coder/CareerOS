# CareerOS AI Project Context

## Purpose
This folder is a compact persistent context layer for local and cloud AI engineering agents. It does not replace `AGENTS.md` or the canonical documents under `docs/`.

## Mandatory read order
1. `AGENTS.md`
2. `docs/21_AI_TO_AI_COORDINATION_PROTOCOL.md`
3. `docs/22_CAREEROS_CURRENT_CONTROL_STATE.md`
4. Relevant architecture/specification/status documents under `docs/`
5. Existing implementation for the subsystem being changed

## Current development line
- Repository: `arunramakantsingh-coder/CareerOS`
- Protected working baseline: `release/v0.2-global-job-intelligence`
- AI tooling/bootstrap work must be isolated from product feature work.

## Source-of-truth model
- GitHub repository = implementation truth.
- Approved project documentation = intent and architecture truth.
- Local execution = runtime truth.
- Human browser/runtime observation = acceptance truth.

## Non-negotiable agent behavior
- Never rebuild an existing subsystem without first inspecting it.
- Prefer the smallest reviewable change.
- Never claim tests, builds, migrations, UI behavior, or runtime health passed unless actually executed and observed.
- Never commit secrets or credentials.
- Do not silently expand scope.
- Do not move to the next milestone until the project verification gate passes.
- Preserve the v0.1 baseline unless an explicitly authorized task says otherwise.

## Standard task lifecycle
`ISSUE -> PLAN -> BRANCH -> IMPLEMENT -> TEST -> REVIEW -> RUNTIME VERIFY -> PR -> MERGE -> RELEASE/STATUS UPDATE`

## Agent handoff contract
Every implementation report must include:
- task/issue identifier
- branch name
- files changed
- migrations/dependency changes
- commands actually executed
- tests actually executed and outcomes
- known failures or unverified items
- commit SHA(s)
- rollback notes when relevant

If any required runtime evidence is missing, status remains `OPEN` or `PENDING`, never `VERIFIED`.
