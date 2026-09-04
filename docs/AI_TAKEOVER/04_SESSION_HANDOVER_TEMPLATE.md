# CareerOS — AI Session Handover Record

Every AI that performs material work must leave this record updated before stopping. Do not depend on chat history.

## Session identity

```text
DATE/TIME:
AI / AGENT:
ROLE:
HUMAN OWNER:

REPOSITORY:
BRANCH:
COMMIT:
BASE / MERGE BASE:
WORKTREE STATE:
```

## Control state

```text
RELEASE:
STAGE:
MILESTONE:
MODULE:
MODULE VERSION:
STATUS: PLANNED / AUTHORIZED / IMPLEMENTING / IMPLEMENTED / EXECUTED / OBSERVED / QA REVIEW / VERIFIED / DEFERRED / SUPERSEDED / RETIRED
```

## Objective

What was authorized in this session?

## Requirements

List the exact functional requirements being implemented or tested.

## Changes

```text
FILES CREATED:
FILES MODIFIED:
FILES DELETED:
DATABASE / MIGRATIONS:
API:
FRONTEND / UI:
INTEGRATIONS:
```

## Evidence

```text
UNIT TESTS:
INTEGRATION TESTS:
API SMOKE:
FRONTEND BUILD:
E2E:
DOCKER / RUNTIME:
BROWSER / HUMAN ACCEPTANCE:
LOGS / SCREENSHOTS:
```

Only record a test as passed if it was actually executed.

## Bugs

For each defect:

```text
BUG ID:
SEVERITY:
EXPECTED:
ACTUAL:
REPRO:
ROOT CAUSE:
FIX:
RETEST:
STATUS:
```

## Decisions

Record material architecture/product decisions here or as a dedicated ADR. Never leave a material decision only in chat.

## Blockers

State exactly what is preventing progress. Include external prerequisites such as provider credentials, browser security restrictions or unavailable APIs.

## What is NOT complete

This section is mandatory. Do not use optimistic wording to hide unfinished work.

## Exact next action

One concrete next action for the next AI/human.

## Handover marker

```text
[CAREEROS: SESSION HANDOVER]
No verification claim is implied by this record unless the status is explicitly VERIFIED and the required evidence is present.
```
