# ChatGPT QA Action Ledger

This file is the shared audit trail for the current M02 reconstruction. It is intentionally kept under `WORKING/` so DeepSeek and ChatGPT can inspect the same control state.

| Seq | Actor | Action | Status |
|---|---|---|---|
| 001 | ChatGPT | Created shared working branch `working/careeros-ai-sync-20260830` from release checkpoint | DONE |
| 002 | ChatGPT | Reconciled uploaded ZIP/current local state against GitHub release state | DONE |
| 003 | ChatGPT | Audited executed DeepSeek M02 script transcript | DONE |
| 004 | ChatGPT | Identified M02 blockers: document persistence, route mismatch, upload contract, validation/security, UI regression | DONE |
| 005 | ChatGPT | Created persistent project memory in ChatGPT Library under `/CareerOS` | DONE |
| 006 | ChatGPT | Created M02 master module/phase/file/acceptance map | DONE |
| 007 | ChatGPT | Established rule: every material coding action must be committed/pushed to WORKING and inspected before next action | ACTIVE |
| 008 | ChatGPT | M02 repair authorization | PENDING DeepSeek repair proposal + ChatGPT code review |

## Required DeepSeek protocol
1. Pull/inspect latest working branch before each batch.
2. Declare exact M02 phase/module/submodule and files touched.
3. Make minimal scoped changes only.
4. Commit and push after each material batch.
5. Update a `WORKING/` status note with commit SHA, changed files, tests run and known issues.
6. Do not modify release branch.
7. Do not implement M03+.

## Required ChatGPT QA protocol
For each DeepSeek batch:
- inspect GitHub diff/changed files;
- trace UI → API client → backend route → schema/service → model → migration/database;
- check reverse dependencies and regression surface;
- inspect tests and scripts before Arun executes them;
- authorize or reject the batch;
- after runtime evidence, verify actual behavior rather than trusting script claims;
- update this ledger.

M02 VERIFIED remains NO until the complete acceptance/stability gate passes.
