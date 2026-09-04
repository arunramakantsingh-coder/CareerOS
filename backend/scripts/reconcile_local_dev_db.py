"""Reconcile the known pre-Alembic CareerOS local development database.

This is intentionally a one-time, explicit repair utility for development databases
that were created with SQLAlchemy ``create_all`` before Alembic became authoritative.
It does not rewrite any Alembic migration and refuses to stamp the database unless
the existing M02 tables required by revision 016 are already present.

After this script succeeds, normal startup uses ``alembic upgrade head``.
"""

from sqlalchemy import inspect, text

from app.core.database import engine

REQUIRED_TABLES = {
    "users",
    "documents",
    "candidate_profiles",
    "external_identities",
    "career_fact_evidence",
    "persona_suggestions",
    "email_connector_accounts",
}


def main() -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names(schema="public"))
    missing = sorted(REQUIRED_TABLES - tables)
    if missing:
        raise SystemExit(
            "Refusing reconciliation: required existing tables are missing: "
            + ", ".join(missing)
        )

    with engine.begin() as connection:
        # These are the only missing schema objects observed in the affected local DB.
        # IF NOT EXISTS makes the repair safe to re-run.
        connection.execute(
            text(
                "ALTER TABLE public.users "
                "ADD COLUMN IF NOT EXISTS role VARCHAR(30) NOT NULL DEFAULT 'user'"
            )
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS idx_users_role ON public.users (role)")
        )

        document_columns = {
            "user_label": "VARCHAR(255)",
            "detected_type": "VARCHAR(80)",
            "classification_reason": "TEXT",
            "verification_status": "VARCHAR(30) NOT NULL DEFAULT 'reported'",
            "processing_stage": "VARCHAR(40) NOT NULL DEFAULT 'uploaded'",
        }
        for name, definition in document_columns.items():
            connection.execute(
                text(
                    f"ALTER TABLE public.documents "
                    f"ADD COLUMN IF NOT EXISTS {name} {definition}"
                )
            )

        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_documents_detected_type "
                "ON public.documents (candidate_id, detected_type)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_documents_verification_status "
                "ON public.documents (candidate_id, verification_status)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_fact_evidence_fact "
                "ON public.career_fact_evidence (candidate_id, fact_type, fact_id)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_fact_evidence_document "
                "ON public.career_fact_evidence (document_id)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_persona_suggestions_user "
                "ON public.persona_suggestions (user_id, status)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_email_connector_user_provider "
                "ON public.email_connector_accounts (user_id, provider)"
            )
        )

        # The old development database has no Alembic history table. Once the
        # schema is reconciled to revision 016, establish that history explicitly.
        connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS public.alembic_version "
                "(version_num VARCHAR(32) NOT NULL)"
            )
        )
        connection.execute(text("DELETE FROM public.alembic_version"))
        connection.execute(
            text(
                "INSERT INTO public.alembic_version (version_num) "
                "VALUES ('016_m02_identity_intelligence')"
            )
        )

    # Final verification after the transaction commits.
    inspector = inspect(engine)
    users_columns = {column["name"] for column in inspector.get_columns("users", schema="public")}
    documents_columns = {
        column["name"] for column in inspector.get_columns("documents", schema="public")
    }
    required_document_columns = {
        "user_label",
        "detected_type",
        "classification_reason",
        "verification_status",
        "processing_stage",
    }
    if "role" not in users_columns:
        raise SystemExit("Reconciliation failed verification: users.role is still missing")
    if not required_document_columns.issubset(documents_columns):
        missing = sorted(required_document_columns - documents_columns)
        raise SystemExit(
            "Reconciliation failed verification: missing document columns: "
            + ", ".join(missing)
        )

    with engine.connect() as connection:
        revision = connection.execute(
            text("SELECT version_num FROM public.alembic_version")
        ).scalar_one()
    if revision != "016_m02_identity_intelligence":
        raise SystemExit(f"Reconciliation failed verification: Alembic revision is {revision!r}")

    print("CareerOS local database reconciled successfully at 016_m02_identity_intelligence")


if __name__ == "__main__":
    main()
