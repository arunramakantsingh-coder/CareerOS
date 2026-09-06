# CareerOS Developer Mode

## Purpose

Developer Mode is a small control layer for building and testing CareerOS. It is not a second application and should not grow into module-specific administration screens.

## What belongs here

- Project Tracker and Bug Tracker entry points.
- Git/version history and recovery guidance.
- Generic runtime diagnostics.
- One generic test-data reset mechanism with scopes.
- Safe links to the GitHub repository and issue history.

## What does not belong here

- Product workflows duplicated for developers.
- A separate developer page for every future module.
- Direct Git history rewriting from the application.
- Secret/token display.
- Automatic data deletion on application restart.

## Reset model

The backend exposes one generic reset operation:

- `career_data` — reset parsed profile facts/evidence and completeness state.
- `documents` — remove uploaded test documents from CareerOS storage.
- `personas` — remove generated persona data.
- `connections` — remove connector test records and clear Gmail mailbox tokens while preserving the Google identity record used for sign-in.
- `all` — combine the above for a clean onboarding test state.

All reset operations are authenticated through the developer role, require explicit UI confirmation, preserve the login account, and create an audit-log entry.

## Git/version recovery

GitHub remains the code and version source of truth. Developer Mode may display runtime version/branch/commit metadata and link to GitHub, but it must not silently reset or rewrite repository history.

Development cadence:

**Baseline → Change → Verify → Commit → Next Change**

A successful functional stage should become a Git recovery point before the next functional area is changed.

GitHub's own branch protection, pull requests and Actions are preferred for repository-level recovery and release controls. citeturn0search7turn0search2
