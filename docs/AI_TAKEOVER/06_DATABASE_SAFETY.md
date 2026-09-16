# CareerOS — AI Database Safety Control

This file is an AI-agent control-plane reference. It is intentionally short; the mandatory operational procedure is `docs/DB_MIGRATION_AND_DATABASE_VALIDATION_PROCEDURE.md`.

## Mandatory rule

Any material change that can affect PostgreSQL structure or Alembic state is a **database-affecting change**.

Before implementation:

1. Inspect Git branch/commit/status.
2. Inspect Alembic graph and current DB revision.
3. Run the read-only database validator.
4. Establish the expected schema change.
5. Protect existing data and PostgreSQL volume.

During implementation:

- Never modify an already-applied migration.
- Never reuse a revision ID.
- Never casually rename a revision ID that may already exist in a database.
- Use an explicit Alembic merge revision for intentional parallel migration branches.
- Do not reset, drop, truncate, downgrade for repair, or recreate the development database.
- Do not silently stamp unknown schema to `head`.

After implementation:

1. Test a fresh database migration.
2. Test the representative existing database state.
3. Run post-migration structural validation.
4. Verify important row counts are preserved.
5. Start the application and run feature smoke tests.
6. Record actual evidence in the live handover.

## Known CareerOS regression

The September 2026 incident involved a historical `017_m02_employment_semantic` identifier while the current graph uses `017_m02_employment_semantic_fields`, combined with a descendant `018_m02_profile_sections` row and a second `018` migration branch.

This is now a permanent compatibility and CI regression case.

## Required tools

```text
backend/scripts/validate_database.py

docs/DB_MIGRATION_AND_DATABASE_VALIDATION_PROCEDURE.md

docs/DB_SCHEMA_BASELINE.md
```

The validator is read-only. Migration execution remains a separate, explicit operation.
