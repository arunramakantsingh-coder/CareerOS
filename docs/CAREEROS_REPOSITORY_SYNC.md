# CareerOS - Repository Synchronization and Troubleshooting Baseline

## Canonical Source

GitHub `main` is the canonical verified baseline. Never assume a local checkout, worktree, ZIP or old pasted source equals GitHub.

## Required Check

```powershell
git fetch --all --prune
git status --short --branch
git branch -vv
git rev-parse HEAD
git rev-parse origin/main
```

## State Classification

```text
SYNCED
AHEAD
BEHIND
DIVERGED
DIRTY
```

## Review Rule

ChatGPT and DeepSeek review the actual branch and commit containing the milestone implementation.

## Troubleshooting Baseline

```text
GitHub verified baseline
        ->
local branch
        ->
local commit
        ->
uncommitted changes
        ->
runtime/environment
        ->
database/migrations
        ->
configuration
```

Do not diagnose a source-code defect until this baseline is established.

## Normal Milestone Flow

```text
GitHub baseline
 ->
DeepSeek reads current branch
 ->
implementation
 ->
PowerShell script from project root
 ->
tests
 ->
feature branch / PR
 ->
ChatGPT reviews actual diff
 ->
fixes if required
 ->
human approval
 ->
merge
 ->
project status update
```

## Safe Upload

Use GitHub when the required information exists there. Upload only local-only artifacts such as sanitized logs, screenshots, local DB evidence, private documents or sanitized configuration. Never upload secrets, `.env`, keys, tokens, `node_modules`, `.next`, `__pycache__`, `.git`, worktrees or caches.
