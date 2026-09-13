# CareerOS — LIVE HANDOVER SNAPSHOT

> Update this file at the end of every material AI session. A new AI must be able to continue from GitHub and runtime evidence without relying on prior chat.

## Snapshot

- Date: 2026-09-13
- Active development branch: `feature/intelligence-provider-gateway-20260912`
- Current branch HEAD: `a6a9b3566c4791753ee36f54de044269738fc0b4`
- Active product release: v0.2 Global Job Intelligence
- Active work: Global Intelligence provider gateway + M02 database migration repair/safety
- Current PR: **#25 — feat(intelligence): add provider-neutral AI gateway + DB safety**
- PR state: OPEN / DRAFT
- Release target: `release/v0.2-global-job-intelligence`
- Overall status: **IMPLEMENTATION PRESENT / LOCAL DATABASE RUNTIME VALIDATION PENDING**

## Current development model

```text
Product Owner
    ↓
Lead AI / QA defines scope and acceptance
    ↓
Coding AI inspects GitHub + control plane
    ↓
Implementation on authorized branch
    ↓
Migration + schema validation when DB-affecting
    ↓
Tests / CI
    ↓
Human pulls exact branch and runs local Docker/browser acceptance
    ↓
Runtime evidence returns to Lead AI
    ↓
QA / release review
```

The human is the local runtime/operator and product owner. The coding AI should make source changes through the authorized repository workflow and provide exact local verification commands.

## Database safety control — permanent

All material PostgreSQL/Alembic changes are governed by:

- `docs/AI_TAKEOVER/06_DATABASE_SAFETY.md`
- `docs/DB_MIGRATION_AND_DATABASE_VALIDATION_PROCEDURE.md`
- `docs/DB_SCHEMA_BASELINE.md`
- `backend/scripts/validate_database.py`

Database validation is now a release gate. Docker startup must not be the first place a migration defect is discovered.

## Current migration graph

```text
016_m02_identity_intelligence
                |
017_m02_employment_semantic_fields
          ______|________________
         /                       \
018_m02_profile_sections   018_global_intelligence_provider_registry
         \                       /
          \_____________________/
                    |
             019_intelligence_registry
```

The historical database state was verified to contain:

```text
017_m02_employment_semantic
018_m02_profile_sections
```

The physical schema already contains the 017 employment semantic columns and 018 profile-section columns. `intelligence_provider_configs` was missing at the time of diagnosis.

The migration bootstrap now contains a narrow compatibility path that verifies the 017 schema before normalizing only Alembic bookkeeping. It must not rerun the 017 schema DDL.

## Database work implemented in this session

- Added legacy revision compatibility in `backend/app/core/migrations.py`.
- Added migration compatibility regression test in `backend/tests/test_migration_bootstrap.py`.
- Added read-only structural validator: `backend/scripts/validate_database.py`.
- Added mandatory procedure: `docs/DB_MIGRATION_AND_DATABASE_VALIDATION_PROCEDURE.md`.
- Added structural baseline/control document: `docs/DB_SCHEMA_BASELINE.md`.
- Added AI-agent database safety control: `docs/AI_TAKEOVER/06_DATABASE_SAFETY.md`.
- Linked database safety controls into `.ai/README.md`.
- Added fresh-DB and legacy-revision migration CI gates.
- Updated PR #25 description to reflect database work.

## Local database evidence before repair

Verified from the user's local environment:

```text
alembic_version:
017_m02_employment_semantic
018_m02_profile_sections
```

Verified schema:

```text
professional_experiences:
client
technologies
industries

candidate_profiles:
projects
accomplishments

intelligence_provider_configs:
missing
```

The backend startup failure was:

```text
RevisionError: Requested revision 018_m02_profile_sections overlaps with
other requested revisions 017_m02_employment_semantic_fields
```

This must be re-tested after pulling the current branch. No destructive DB operation has been authorized.

## Required local acceptance after pull

From:

```powershell
PS C:\Projects\v0.2-global-job-intelligence>
```

First verify repository state and protected files remain untouched.

Then run the read-only pre-migration validator:

```powershell
docker compose run --rm backend python scripts/validate_database.py --phase pre-migration
```

Then rebuild/start the backend so the controlled migration compatibility path can execute.

After startup/migration, run:

```powershell
docker compose run --rm backend python scripts/validate_database.py --phase post-migration
```

Then verify:

```powershell
docker compose run --rm backend python -c "from alembic.config import Config; from alembic import command; cfg=Config('alembic.ini'); command.current(cfg, verbose=True)"
```

Expected final migration state:

```text
019_intelligence_registry
```

Also verify:

- `intelligence_provider_configs` exists;
- important application row counts are unchanged;
- backend starts;
- `http://localhost:8000/api/v1/health` responds;
- frontend remains usable;
- relevant Intelligence provider diagnostics work;
- protected untracked files remain untouched.

## Safety restrictions

Never use during this repair:

```text
docker compose down -v
DROP TABLE
TRUNCATE
application-data DELETE
alembic downgrade
PostgreSQL volume recreation
CV re-upload
```

Protected untracked files:

```text
backend/backend-openapi.json
cv-extracted.txt
openapi-check.json
```

## Product safety

- v0.1 remains frozen.
- Do not merge PR #25 automatically.
- Do not claim runtime verification without actual local output.
- Do not move to later product modules merely because implementation exists.

## Exact next action

Pull the current PR #25 branch locally, rebuild the backend, and return the actual output from the pre/post database validation, migration current state, backend health, and `git status --short`. Do not manually edit the database before the compatibility path has been tested.
