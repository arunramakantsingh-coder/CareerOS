"""Safe database migration bootstrap for CareerOS.

Alembic is the authoritative schema mechanism. The application must never use
SQLAlchemy ``create_all`` to synchronize an existing database because it does
not apply column/index/constraint changes from later revisions.

This module handles three cases:
* a new database: run the complete Alembic graph to head;
* a legacy database that predates ``alembic_version``: identify a known schema
  fingerprint, stamp that exact baseline, then upgrade to head;
* a database containing the historical M02 employment revision identifier:
  verify the 017 schema is already present, normalize only the Alembic
  bookkeeping, then continue with the current graph.

Unknown or unsafe database states fail closed rather than being blindly
stamped, downgraded, or recreated.
"""

from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text

from app.core.database import engine
from app.core.config import settings

logger = logging.getLogger(__name__)

HEAD = "019_intelligence_registry"
BASELINE_014 = "014_m02_identity_career_intake"
BASELINE_015 = "015_document_vault_enhancement"

# Historical revision IDs that were actually used by earlier CareerOS
# databases. These are aliases for bookkeeping only; they must never cause the
# corresponding schema migration to execute a second time.
LEGACY_REVISION_ALIASES = {
    "017_m02_employment_semantic": "017_m02_employment_semantic_fields",
}

EMPLOYMENT_SEMANTIC_COLUMNS = {"client", "technologies", "industries"}


def _alembic_config() -> Config:
    """Build an Alembic config that works from the backend container."""
    backend_dir = Path(__file__).resolve().parents[2]
    cfg = Config(str(backend_dir / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))
    cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    return cfg


def _has_version_table() -> bool:
    inspector = inspect(engine)
    return "alembic_version" in inspector.get_table_names()


def _get_version_rows() -> list[str]:
    with engine.connect() as connection:
        return [
            str(row[0])
            for row in connection.execute(
                text("SELECT version_num FROM alembic_version ORDER BY version_num")
            )
        ]


def _has_columns(table: str, columns: set[str]) -> bool:
    inspector = inspect(engine)
    if table not in inspector.get_table_names():
        return False
    actual = {column["name"] for column in inspector.get_columns(table)}
    return columns.issubset(actual)


def _has_tables(tables: set[str]) -> bool:
    actual = set(inspect(engine).get_table_names())
    return tables.issubset(actual)


def _revision_is_ancestor(script: ScriptDirectory, ancestor: str, revision: str) -> bool:
    """Return True when ``ancestor`` occurs in ``revision``'s parent chain."""
    if ancestor == revision:
        return True

    seen: set[str] = set()
    pending = [revision]
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        if current == ancestor:
            return True
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
    return False


def _normalize_legacy_revision_state(cfg: Config) -> None:
    """Normalize known historical revision IDs without rerunning schema DDL.

    This function is deliberately narrow. It only touches ``alembic_version``
    when a known historical ID is present and its schema fingerprint proves
    that the corresponding migration already ran. It does not repair arbitrary
    migration drift.
    """
    revisions = _get_version_rows()
    legacy_present = [rev for rev in revisions if rev in LEGACY_REVISION_ALIASES]
    if not legacy_present:
        return

    if not _has_columns("professional_experiences", EMPLOYMENT_SEMANTIC_COLUMNS):
        raise RuntimeError(
            "Legacy Alembic revision 017_m02_employment_semantic is present, "
            "but professional_experiences is missing one or more of client, "
            "technologies, industries. Refusing to rewrite migration "
            "bookkeeping because the historical schema cannot be proven applied."
        )

    script = ScriptDirectory.from_config(cfg)
    normalized = set(revisions)
    for legacy in legacy_present:
        current = LEGACY_REVISION_ALIASES[legacy]
        normalized.discard(legacy)
        normalized.add(current)

    # Alembic normally stores only the leaf revisions in alembic_version. The
    # affected legacy database can contain both the old 017 row and a descendant
    # such as 018_m02_profile_sections. After aliasing, the 017 row would still
    # be an ancestor of that descendant and would make ``upgrade head`` fail.
    # Collapse only ancestors introduced by this explicit legacy normalization.
    for candidate in list(normalized):
        for other in normalized:
            if candidate == other:
                continue
            if _revision_is_ancestor(script, candidate, other):
                normalized.discard(candidate)
                break

    if normalized == set(revisions):
        return

    logger.warning(
        "Normalizing legacy Alembic bookkeeping only: %s -> %s",
        revisions,
        sorted(normalized),
    )
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM alembic_version"))
        for revision in sorted(normalized):
            connection.execute(
                text("INSERT INTO alembic_version (version_num) VALUES (:revision)"),
                {"revision": revision},
            )


def _detect_legacy_baseline() -> str | None:
    """Return a revision only when the existing schema has a known fingerprint."""
    tables = set(inspect(engine).get_table_names())
    if not tables:
        return None

    # 016 fingerprint: the role column plus all tables/columns introduced by
    # the M02 identity-intelligence revision.
    if (
        _has_columns("users", {"role"})
        and _has_tables({"career_fact_evidence", "persona_suggestions", "email_connector_accounts"})
        and _has_columns(
            "documents",
            {
                "content_hash",
                "issuer",
                "issue_date",
                "expiry_date",
                "document_number",
                "document_type",
                "batch_id",
                "is_zip_content",
                "parent_zip_id",
                "classification_confidence",
            },
        )
    ):
        return "016_m02_identity_intelligence"

    # 015 fingerprint: 014's M02 tables exist and all fields added by 015 are
    # present, but 016's role column is not yet present.
    if (
        _has_tables(
            {
                "external_identities",
                "candidate_profiles",
                "professional_experiences",
                "candidate_skills",
                "candidate_certifications",
                "candidate_educations",
                "documents",
                "extraction_results",
                "extraction_fields",
            }
        )
        and _has_columns(
            "documents",
            {
                "content_hash",
                "issuer",
                "issue_date",
                "expiry_date",
                "document_number",
                "document_type",
                "batch_id",
                "is_zip_content",
                "parent_zip_id",
                "classification_confidence",
            },
        )
    ):
        return BASELINE_015

    # 014 fingerprint: the M02 intake tables exist, but the 015 document
    # enhancement fields do not.
    if _has_tables(
        {
            "external_identities",
            "candidate_profiles",
            "professional_experiences",
            "candidate_skills",
            "candidate_certifications",
            "candidate_educations",
            "documents",
            "extraction_results",
            "extraction_fields",
        }
    ):
        return BASELINE_014

    return None


def reconcile_database() -> None:
    """Bring the database to the Alembic head without destroying data."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    cfg = _alembic_config()

    if _has_version_table():
        _normalize_legacy_revision_state(cfg)
        logger.info("Alembic version table detected; upgrading database to %s", HEAD)
        command.upgrade(cfg, "head")
        return

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if not tables:
        logger.info("Empty database detected; applying Alembic migrations to %s", HEAD)
        command.upgrade(cfg, "head")
        return

    baseline = _detect_legacy_baseline()
    if baseline is None:
        raise RuntimeError(
            "CareerOS database has no alembic_version table and does not match a "
            "known migration baseline. Refusing to stamp or modify the schema "
            "automatically. Inspect the schema and create an explicit recovery "
            "migration before starting the API."
        )

    if baseline == "016_m02_identity_intelligence":
        logger.warning("Legacy schema matches Alembic 016; recording revision %s", baseline)
        command.stamp(cfg, baseline)
        command.upgrade(cfg, "head")
        return

    logger.warning("Legacy schema detected at %s; recording that exact baseline", baseline)
    command.stamp(cfg, baseline)
    command.upgrade(cfg, "head")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    reconcile_database()
