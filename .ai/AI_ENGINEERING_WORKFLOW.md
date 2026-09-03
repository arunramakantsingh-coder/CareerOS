# CareerOS AI Engineering Workflow

## Goal
Use local AI agents as controlled engineers working inside the real repository while Git/GitHub remain the audit trail and project control plane.

## Roles
- Human owner: approves scope, destructive actions, merges, releases, and acceptance.
- Lead/QA AI: architecture, planning, review, verification criteria, scope control.
- Local coding agent (Cline first): repository inspection, implementation, terminal commands, tests, and change summaries.
- Optional autonomous agent (OpenHands): larger isolated tasks only after the Cline workflow is stable.

## Branch policy
Never implement directly on `main` or a release baseline.

Use:
- `feature/<issue>-<short-name>`
- `bugfix/<issue>-<short-name>`
- `chore/<short-name>`
- `docs/<short-name>`

## Issue policy
Every material change should map to one GitHub Issue containing:
- problem/goal
- acceptance criteria
- in-scope items
- explicitly out-of-scope items
- test/runtime evidence required
- security/data implications where applicable

Recommended labels:
`type:feature`, `type:bug`, `type:security`, `type:tech-debt`, `priority:p0..p3`, `status:blocked`, `needs:runtime-verification`.

## Agent execution policy
1. Read `AGENTS.md` and `.ai/PROJECT_CONTEXT.md` first.
2. Inspect affected code before proposing a change.
3. Produce a concise implementation plan.
4. Confirm working tree and active branch.
5. Make the smallest safe change.
6. Run focused tests first, then regression/build checks appropriate to the change.
7. Show the exact diff/changed files.
8. Do not commit generated secrets, local databases, environment credentials, build caches, or dependency folders.
9. Create an atomic commit with the issue/task identifier.
10. Prepare PR evidence.

## Verification gate
A milestone/change is not complete until applicable checks pass:
- backend health
- frontend availability
- database health/migrations
- changed API checks
- changed UI checks
- regression tests
- logs checked for new errors
- Git working tree understood
- local and remote commit/branch state understood

Use project-specific runtime endpoints from the canonical docs. For the current CareerOS control state, localhost frontend and backend health are part of the minimum runtime gate.

## Pull request template
PR description should contain:

### Goal
What this change achieves.

### Scope
What changed and what deliberately did not change.

### Evidence
Commands/tests/runtime checks actually executed.

### Risk
Known risks, migration impact, compatibility concerns.

### Rollback
How to reverse safely.

### Verification
`QA: PASS/PENDING/FAIL`
`RUNTIME: PASS/PENDING/FAIL`
`STABILITY: PASS/PENDING/FAIL`

## Release policy
- Use semantic versioning where the existing product version architecture permits it.
- Release only from an explicitly approved commit.
- Tag the exact verified commit.
- Record release notes: features, fixes, migrations, known issues, rollback notes.
- Never infer release readiness from code completion alone.

## Bug policy
For every bug:
1. reproduce
2. capture evidence
3. classify severity/scope
4. create or link issue
5. isolate fix branch
6. add/adjust regression test when feasible
7. verify the original reproduction no longer fails
8. verify adjacent functionality
9. document any remaining risk
