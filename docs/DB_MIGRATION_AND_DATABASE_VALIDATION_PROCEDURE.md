# CareerOS — Database Migration & Validation Procedure

**Status:** Mandatory engineering procedure  
**Scope:** All CareerOS branches and milestones that can affect PostgreSQL schema or migration state

## 1. Purpose

CareerOS uses Alembic as the authoritative database schema mechanism. Major feature work must never make the application discover database incompatibility only at startup.

This procedure exists because migration failures have previously occurred when feature branches changed migration history independently, including a historical revision-ID change and concurrent `018` branches.

The rule is simple:

> **Every material database change must be validated against both the migration graph and the actual database before the application is accepted.**

## 2. Source-of-truth order

When database state is being investigated, use this order:

1. Actual PostgreSQL structure and `alembic_version`.
2. Actual Alembic migration graph in `backend/alembic/versions/`.
3. Actual runtime/test output.
4. Current control-plane/handover documentation.
5. Historical documentation.

Never assume that a migration filename, branch name, or old handover accurately represents the live database.

## 3. Non-negotiable data protection

Database work MUST NOT use any of the following unless the Product Owner explicitly authorizes a destructive operation for a disposable environment:

- database reset
- `docker compose down -v`
- `DROP TABLE`
- `TRUNCATE`
- destructive `DELETE`
- Alembic downgrade as a repair mechanism
- PostgreSQL volume recreation
- deletion/recreation of Career Vault employment records
- deletion/recreation of uploaded documents
- deletion/recreation of profile or identity records

Never modify a database to make a migration pass without first proving what the change does.

## 4. Protected local files

AI/coding agents must not overwrite unrelated protected untracked files. The current development workflow specifically protects:

```text
backend/backend-openapi.json
cv-extracted.txt
openapi-check.json
```

Always inspect `git status` before implementation.

## 5. Before a major feature

A change is considered database-risky when it introduces or changes:

- tables
- columns
- data types
- primary/foreign keys
- unique/check constraints
- indexes
- enums/sequences/views/triggers
- persistence models
- document/profile/Career Vault structures
- provider configuration persistence
- migration files
- migration branches or merge revisions

Before implementation:

1. Confirm branch and commit.
2. Run `git status`.
3. Confirm protected untracked files.
4. Inspect Alembic heads.
5. Inspect Alembic current revision(s).
6. Inspect all migration parents and merge points.
7. Run the read-only database validator.
8. Capture important application-table row counts.
9. Record material discrepancies before changing code.

## 6. Migration authoring rules

Every schema change MUST:

- use a new Alembic revision;
- have a unique revision ID;
- have a valid `down_revision`;
- include explicit `upgrade()` and `downgrade()` behavior appropriate to the change;
- avoid modifying an already-applied migration;
- preserve existing application data;
- be tested against a fresh database;
- be tested against a representative existing database state;
- pass the repository migration-graph validator.

### Revision IDs are permanent history

A revision ID is database history, not a filename. Never casually rename an Alembic revision that may already have been applied to a database.

If a historical ID must be replaced:

1. search Git history;
2. identify the old ID and its schema operation;
3. inspect databases that may contain the old ID;
4. prove whether the schema operation already ran;
5. add a narrow compatibility path if required;
6. test both the legacy state and a fresh database.

The compatibility path must distinguish a **legacy bookkeeping identifier** from an **actually missing schema migration**.

## 7. Parallel branches and merge revisions

Two feature branches must never independently introduce the same revision ID.

When two migrations intentionally branch from the same parent, the final graph must explicitly represent that branch and merge it with a merge revision.

Current CareerOS example:

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

A merge revision should not repeat schema operations. Its purpose is to reconcile migration history.

## 8. Required read-only database audit

The validator/procedure must inspect, as applicable:

- schemas
- tables
- columns and data types
- nullable/default metadata
- primary keys
- foreign keys
- unique constraints
- check constraints
- indexes
- enum types
- sequences
- views
- triggers
- `alembic_version`
- migration-owned schema objects
- important table row counts

Do not dump user data or document contents into the repository.

## 9. Database vs migration reconciliation

Classify differences as:

| Classification | Meaning | Action |
|---|---|---|
| EXPECTED | Schema is already at the expected state | Continue |
| MISSING | Required schema object is not present | Apply the correct migration |
| LEGACY | Known historical revision/bookkeeping state | Use explicit compatibility handling |
| DRIFT | Schema differs from migration expectation | Stop and investigate |
| DANGEROUS | Automated repair could risk data | Stop and require review |

Never treat an arbitrary schema mismatch as a reason to stamp `head`.

## 10. Startup migration gate

Application startup must use the migration bootstrap and must not call SQLAlchemy `Base.metadata.create_all()` to synchronize an existing database.

Before normal upgrade, the migration bootstrap should reject:

- unknown revision IDs;
- broken migration parents;
- unexpected migration graph states;
- duplicate/overlapping current revisions;
- missing required schema for a known legacy compatibility path;
- dangerous or unexplained drift.

Only narrowly defined, proven legacy bookkeeping normalization may occur automatically.

## 11. Validation commands

From the repository root:

```powershell
# Repository state
 git status --short
 git branch --show-current
 git rev-parse HEAD

# Migration graph
 docker compose run --rm backend python -c "from alembic.config import Config; from alembic import command; cfg=Config('alembic.ini'); command.heads(cfg, verbose=True)"

# Current DB revision
 docker compose run --rm backend python -c "from alembic.config import Config; from alembic import command; cfg=Config('alembic.ini'); command.current(cfg, verbose=True)"

# Read-only database validation
 docker compose run --rm backend python scripts/validate_database.py --phase pre-migration
```

After migration:

```powershell
 docker compose run --rm backend python scripts/validate_database.py --phase post-migration
```

Then run the application and feature smoke tests.

## 12. Fresh-database test

Every database-affecting change must be tested against a disposable empty PostgreSQL database in CI or an explicitly disposable local environment.

The fresh database must reach the current Alembic head without manual schema creation.

## 13. Existing-database test

Every database-affecting change must also be tested against a representative existing database state.

At minimum verify:

- existing tables remain present;
- existing important rows remain present;
- migration state becomes a valid Alembic state;
- new schema objects appear exactly once;
- no old migration is rerun;
- application startup succeeds.

## 14. Expand / migrate / contract

For potentially destructive changes, prefer:

```text
1. EXPAND
   Add compatible schema.

2. MIGRATE
   Backfill/transform existing records safely.

3. VALIDATE
   Verify counts, constraints and application behavior.

4. SWITCH
   Move application reads/writes to the new representation.

5. CONTRACT
   Remove obsolete structures only after explicit validation.
```

## 15. Baseline maintenance

`docs/DB_SCHEMA_BASELINE.md` is the structural reference for the current validated database state.

It must contain structural information only. Never store:

- passwords
- API keys
- tokens
- CV contents
- personal document contents
- raw production data

When a major schema migration is intentionally accepted, update the baseline with the new migration head and structural changes.

## 16. CI gate

Database CI should validate:

1. duplicate revision IDs;
2. broken migration parents;
3. expected Alembic heads;
4. fresh PostgreSQL migration to head;
5. representative legacy/existing migration state where applicable;
6. post-migration structural validation;
7. application startup/tests.

A migration failure is a release blocker, not a runtime warning.

## 17. Completion evidence

A database-affecting task is complete only when the implementation report contains:

- branch and commit;
- migration graph result;
- DB revision before and after;
- structural validation result;
- migrations executed;
- important row-count preservation result;
- application health result;
- relevant feature smoke-test result;
- exact files changed;
- known risks or unresolved drift.

Never claim a migration passed without actual command output.

## 18. Current incident reference

The current Intelligence Gateway branch exposed a historical M02 revision mismatch:

```text
legacy DB:
017_m02_employment_semantic
018_m02_profile_sections

current graph:
017_m02_employment_semantic_fields
018_m02_profile_sections
018_global_intelligence_provider_registry
019_intelligence_registry
```

The physical 017 employment columns and 018 profile-section columns were already present. The Intelligence provider registry was missing. Therefore the safe repair is migration-bookkeeping compatibility followed by application of only the missing Intelligence schema and merge point.

This incident is now a permanent regression case for migration CI.
