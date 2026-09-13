"""Read-only CareerOS database and Alembic validation utility.

Usage:
    python scripts/validate_database.py --phase pre-migration
    python scripts/validate_database.py --phase post-migration

This command never changes the database. It is intended for local validation and
CI gates before/after migration execution.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text

from app.core.database import engine
from app.core.config import settings

HEAD = "019_intelligence_registry"
LEGACY_ALIASES = {
    "017_m02_employment_semantic": "017_m02_employment_semantic_fields",
}
REQUIRED_COLUMNS = {
    "professional_experiences": {"client", "technologies", "industries"},
    "candidate_profiles": {"projects", "accomplishments"},
}
POST_MIGRATION_TABLES = {"intelligence_provider_configs"}
IMPORTANT_TABLES = {
    "users",
    "candidate_profiles",
    "professional_experiences",
    "candidate_skills",
    "candidate_certifications",
    "candidate_educations",
    "documents",
    "extraction_results",
    "extraction_fields",
    "external_identities",
    "persona_suggestions",
    "career_fact_evidence",
    "email_connector_accounts",
    "intelligence_provider_configs",
}


def config() -> Config:
    backend_dir = Path(__file__).resolve().parents[1]
    cfg = Config(str(backend_dir / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))
    cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    return cfg


def script_directory() -> ScriptDirectory:
    return ScriptDirectory.from_config(config())


def ancestor(script: ScriptDirectory, candidate: str, revision: str) -> bool:
    if candidate == revision:
        return True
    seen: set[str] = set()
    pending = [revision]
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        node = script.get_revision(current)
        if node is None:
            return False
        parents = node.down_revision
        if parents is None:
            continue
        if isinstance(parents, tuple):
            pending.extend(parents)
        else:
            pending.append(parents)
        if candidate in pending:
            return True
    return False


def current_revisions() -> list[str]:
    inspector = inspect(engine)
    if "alembic_version" not in inspector.get_table_names():
        return []
    with engine.connect() as connection:
        return [
            str(row[0])
            for row in connection.execute(
                text("SELECT version_num FROM alembic_version ORDER BY version_num")
            )
        ]


def check_graph() -> list[str]:
    errors: list[str] = []
    script = script_directory()
    revisions = list(script.walk_revisions())
    revision_ids = [revision.revision for revision in revisions]
    duplicates = [revision for revision, count in __import__("collections").Counter(revision_ids).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate revision IDs: {duplicates}")

    missing_parents: list[str] = []
    for revision in revisions:
        parents = revision.down_revision
        parents = () if parents is None else (parents if isinstance(parents, tuple) else (parents,))
        for parent in parents:
            if script.get_revision(parent) is None:
                missing_parents.append(f"{revision.revision}->{parent}")
    if missing_parents:
        errors.append(f"missing migration parents: {missing_parents}")

    heads = list(script.get_heads())
    if heads != [HEAD]:
        errors.append(f"unexpected migration heads: {heads}; expected [{HEAD}]")
    return errors


def check_current_state(phase: str) -> list[str]:
    errors: list[str] = []
    revisions = current_revisions()
    script = script_directory()

    if not revisions:
        if "alembic_version" in inspect(engine).get_table_names():
            # A version table without rows is not a valid application state.
            errors.append("alembic_version exists but contains no revision")
        return errors

    unknown = [revision for revision in revisions if script.get_revision(revision) is None and revision not in LEGACY_ALIASES]
    if unknown:
        errors.append(f"unknown Alembic revision(s): {unknown}")

    normalized = [LEGACY_ALIASES.get(revision, revision) for revision in revisions]
    for index, candidate in enumerate(normalized):
        for other in normalized[index + 1 :]:
            if candidate == other:
                errors.append(f"duplicate effective Alembic revision state: {candidate}")
            elif script.get_revision(candidate) and script.get_revision(other):
                if ancestor(script, candidate, other) or ancestor(script, other, candidate):
                    # A known legacy alias may coexist with a descendant before
                    # migrations.py normalizes the bookkeeping. This is the one
                    # intentionally supported pre-migration compatibility state.
                    legacy_pair = (
                        candidate == LEGACY_ALIASES.get(revisions[index], "")
                        or other in LEGACY_ALIASES.values()
                    )
                    if phase == "pre-migration" and legacy_pair:
                        continue
                    errors.append(f"overlapping current revisions: {candidate}, {other}")

    if phase == "post-migration" and normalized != [HEAD]:
        errors.append(f"post-migration database is not at {HEAD}: {revisions}")
    return errors


def schema_inventory() -> dict[str, object]:
    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names())
    inventory: dict[str, object] = {"tables": tables, "table_details": {}}
    details: dict[str, object] = {}
    for table in tables:
        details[table] = {
            "columns": [
                {
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": bool(column.get("nullable", True)),
                    "default": str(column.get("default")) if column.get("default") is not None else None,
                }
                for column in inspector.get_columns(table)
            ],
            "primary_key": inspector.get_pk_constraint(table),
            "foreign_keys": inspector.get_foreign_keys(table),
            "unique_constraints": inspector.get_unique_constraints(table),
            "check_constraints": inspector.get_check_constraints(table),
            "indexes": inspector.get_indexes(table),
        }
    inventory["table_details"] = details
    try:
        inventory["enums"] = inspector.get_enums()
    except (AttributeError, NotImplementedError):
        inventory["enums"] = []
    try:
        inventory["sequences"] = inspector.get_sequence_names()
    except (AttributeError, NotImplementedError):
        inventory["sequences"] = []
    try:
        inventory["views"] = inspector.get_view_names()
    except (AttributeError, NotImplementedError):
        inventory["views"] = []
    return inventory


def check_required_schema(phase: str) -> list[str]:
    if phase == "pre-migration":
        return []
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    errors: list[str] = []
    for table, required in REQUIRED_COLUMNS.items():
        if table not in tables:
            errors.append(f"required table missing: {table}")
            continue
        actual = {column["name"] for column in inspector.get_columns(table)}
        missing = sorted(required - actual)
        if missing:
            errors.append(f"{table} missing required columns: {missing}")
    for table in sorted(POST_MIGRATION_TABLES):
        if table not in tables:
            errors.append(f"required post-migration table missing: {table}")
    return errors


def row_counts() -> dict[str, int]:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    counts: dict[str, int] = {}
    with engine.connect() as connection:
        for table in sorted(IMPORTANT_TABLES & tables):
            quoted = '"' + table.replace('"', '""') + '"'
            counts[table] = int(connection.execute(text(f"SELECT count(*) FROM {quoted}")).scalar_one())
    return counts


def print_inventory(inventory: dict[str, object]) -> None:
    print("\nSCHEMA INVENTORY")
    print("================")
    for table in inventory["tables"]:  # type: ignore[index]
        details = inventory["table_details"][table]  # type: ignore[index]
        print(f"\nTABLE {table}")
        print("  columns:")
        for column in details["columns"]:  # type: ignore[index]
            print(
                f"    - {column['name']} :: {column['type']} "
                f"nullable={column['nullable']} default={column['default']}"
            )
        print(f"  primary_key: {details['primary_key']}")  # type: ignore[index]
        print(f"  foreign_keys: {details['foreign_keys']}")  # type: ignore[index]
        print(f"  unique_constraints: {details['unique_constraints']}")  # type: ignore[index]
        print(f"  check_constraints: {details['check_constraints']}")  # type: ignore[index]
        print(f"  indexes: {details['indexes']}")  # type: ignore[index]
    print(f"\nenums: {inventory['enums']}")
    print(f"sequences: {inventory['sequences']}")
    print(f"views: {inventory['views']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only CareerOS database validator")
    parser.add_argument("--phase", choices=("pre-migration", "post-migration"), default="post-migration")
    parser.add_argument("--inventory", action="store_true", help="print the complete structural inventory")
    args = parser.parse_args()

    print(f"CareerOS DB validation: {args.phase}")
    print(f"DATABASE_URL: {settings.DATABASE_URL.split('@')[-1]}")

    errors = check_graph()
    errors.extend(check_current_state(args.phase))
    errors.extend(check_required_schema(args.phase))

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    print(f"[PASS] Database reachable; tables={len(tables)}")

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        print("\nDatabase validation FAILED. No database mutation was performed.")
        return 1

    print("[PASS] Migration graph")
    print(f"[PASS] Alembic revision state: {current_revisions() or 'empty database'}")
    print("[PASS] Required schema checks")

    counts = row_counts()
    print("[PASS] Important table row counts (read-only):")
    for table, count in counts.items():
        print(f"  {table}: {count}")

    if args.inventory:
        print_inventory(schema_inventory())

    print("\nDATABASE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
