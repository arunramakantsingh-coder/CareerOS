# CareerOS — Git / Branch / Release Control Contract

## Canonical principle

GitHub is the canonical implementation repository. A branch name is never proof of freshness. Always inspect commit ancestry.

## Release lines

| Line | Meaning | Rule |
|---|---|---|
| `release/v0.1-personal-job-interview-copilot` | frozen v0.1 baseline | do not modify for v0.2 feature work |
| `release/v0.2-global-job-intelligence` | v0.2 release baseline | stable integration target |
| `working/*` | active milestone implementation | temporary, testable work |
| `feature/*` | focused feature branch | one feature/module |
| `backup/*` | immutable safety checkpoint | never use as a development branch |
| `integration/*` | controlled integration line | only after feature review |

## Required workflow

```text
Current verified/release baseline
        ↓
backup checkpoint
        ↓
versioned working/feature branch
        ↓
implementation
        ↓
local tests + runtime evidence
        ↓
GitHub PR / review
        ↓
QA decision
        ↓
integration/release
```

## Branch reconciliation rules

Before using an existing branch:

```text
git fetch --all --prune
git branch -a
git log --oneline --decorate --graph --all
git status
```

For GitHub-side review, compare the candidate branch against the intended baseline and record:

- merge base
- ahead/behind counts
- unique commits
- changed files
- current HEAD SHA

If a branch is diverged, do not treat it as the next version automatically.

## Current documented divergence

As of 2026-09-03:

```text
profile branch:
working/m02-profile-builder-v1.3-20260902 @ a3dc548

live interview branch:
working/live-interview-workspace-v0.2.2-20260902 @ 29ec546

comparison:
DIVERGED
live branch: +1 / -16 against profile branch
merge base: 9bd4d80
```

The live-interview branch therefore requires reconciliation before integration.

## Commit discipline

Commit messages should identify the intent and module, for example:

```text
feat(profile): add manual employment section
fix(vault): normalize validation error payloads
feat(auth): add LinkedIn OIDC callback handling
docs(control): record M02 handover state
```

Do not hide unrelated changes inside a milestone commit.

## Backup discipline

Before risky changes create a branch such as:

`backup/<module>-<purpose>-YYYYMMDD`

The backup must point to the exact pre-change commit. Never overwrite it.

## Verification discipline

A commit can be:

```text
IMPLEMENTED
TESTED
OBSERVED
QA REVIEW
VERIFIED
```

These are not interchangeable. `VERIFIED` requires actual evidence and reviewer authorization.

## Pull instructions for the human

When a milestone is ready for local testing, provide:

```powershell
git fetch --all --prune
git switch <exact-branch>
git pull --ff-only origin <exact-branch>
git log -1 --oneline
git status
```

Then run the documented Docker/runtime checks for that milestone.

## Never

- force-push a shared release line to hide history;
- delete a historical version record;
- merge a stale feature branch just because it has a higher version number;
- overwrite v0.1;
- use a local ZIP or temporary folder as the canonical source;
- claim a release is verified without runtime evidence.
