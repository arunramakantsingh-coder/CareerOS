"""Safe database migration bootstrap for CareerOS.

Alembic is the authoritative schema mechanism.  The application must never use
SQLAlchemy ``create_all`` to synchronize an existing database because it does
not apply column/index/constraint changes from later revisions.

This module handles two cases:
* a new database: run the complete Alembic graph to head;
* a legacy database that predates ``alembic_version``: identify a known schema
  fingerprint, stamp that exact baseline, then upgrade to head.

Unknown legacy schemas fail closed rather than being blindly stamped to head.
"""

from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from app.core.database import engine
from app.core.config import settings

logger = logging.getLogger(__name__)

HEAD = "016_m02_identity_intelligence"
BASELINE_014 = "014_m02_identity_career_intake"
BASELINE_015 = "015_document_vault_enhancement"


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


def _has_columns(table: str, columns: set[str]) -> bool:
    inspector = inspect(engine)
    if table not in inspector.get_table_names():
        return False
    actual = {column["name"] for column in inspector.get_columns(table)}
    return columns.issubset(actual)


def _has_tables(tables: set[str]) -> bool:
    actual = set(inspect(engine).get_table_names())
    return tables.issubset(actual)


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
        return HEAD

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

    if baseline == HEAD:
        logger.warning("Legacy schema matches Alembic head; recording revision %s", HEAD)
        command.stamp(cfg, HEAD)
        return

    logger.warning("Legacy schema detected at %s; recording that exact baseline", baseline)
    command.stamp(cfg, baseline)
    command.upgrade(cfg, "head")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    reconcile_database()
