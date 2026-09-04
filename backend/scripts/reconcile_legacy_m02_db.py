"""Safely reconcile the known pre-Alembic M02 development database.

This is intentionally NOT a replacement for Alembic migrations. It handles one
legacy state only: an existing CareerOS database with no alembic_version table
where M02 (016) tables were created but part of the 016 ALTER/INDEX work is
missing. Fresh databases are left untouched and are initialized by Alembic.
"""
from __future__ import annotations

import os
import sys

import psycopg2


REQUIRED_016_TABLES = {
    "career_fact_evidence",
    "persona_suggestions",
    "email_connector_accounts",
}


def main() -> int:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    conn = psycopg2.connect(database_url)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT to_regclass('public.alembic_version') IS NOT NULL, "
                "to_regclass('public.users') IS NOT NULL, "
                "to_regclass('public.documents') IS NOT NULL"
            )
            has_version, has_users, has_documents = cur.fetchone()

            # Fresh/normal Alembic databases must be handled by Alembic.
            if has_version or not (has_users and has_documents):
                conn.rollback()
                return 0

            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name = ANY(%s)",
                (list(REQUIRED_016_TABLES),),
            )
            existing = {row[0] for row in cur.fetchall()}
            if existing != REQUIRED_016_TABLES:
                conn.rollback()
                return 0

            # Verify this is the known partial-016 state before mutating anything.
            cur.execute(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name='users' AND column_name='role'"
            )
            role_exists = cur.fetchone()[0] == 1

            cur.execute(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name='documents' "
                "AND column_name IN ('user_label','detected_type','classification_reason',"
                "'verification_status','processing_stage')"
            )
            document_016_count = cur.fetchone()[0]

            if role_exists or document_016_count != 0:
                conn.rollback()
                return 0

            cur.execute(
                "ALTER TABLE public.users ADD COLUMN role VARCHAR(30) NOT NULL DEFAULT 'user'"
            )
            cur.execute("CREATE INDEX idx_users_role ON public.users (role)")

            cur.execute("ALTER TABLE public.documents ADD COLUMN user_label VARCHAR(255)")
            cur.execute("ALTER TABLE public.documents ADD COLUMN detected_type VARCHAR(80)")
            cur.execute("ALTER TABLE public.documents ADD COLUMN classification_reason TEXT")
            cur.execute(
                "ALTER TABLE public.documents ADD COLUMN verification_status VARCHAR(30) "
                "NOT NULL DEFAULT 'reported'"
            )
            cur.execute(
                "ALTER TABLE public.documents ADD COLUMN processing_stage VARCHAR(40) "
                "NOT NULL DEFAULT 'uploaded'"
            )
            cur.execute(
                "CREATE INDEX idx_documents_detected_type "
                "ON public.documents (candidate_id, detected_type)"
            )
            cur.execute(
                "CREATE INDEX idx_documents_verification_status "
                "ON public.documents (candidate_id, verification_status)"
            )
            cur.execute(
                "CREATE INDEX idx_fact_evidence_fact "
                "ON public.career_fact_evidence (candidate_id, fact_type, fact_id)"
            )
            cur.execute(
                "CREATE INDEX idx_fact_evidence_document "
                "ON public.career_fact_evidence (document_id)"
            )
            cur.execute(
                "CREATE INDEX idx_persona_suggestions_user "
                "ON public.persona_suggestions (user_id, status)"
            )
            cur.execute(
                "CREATE INDEX idx_email_connector_user_provider "
                "ON public.email_connector_accounts (user_id, provider)"
            )

            # Establish Alembic tracking only after the exact known partial state
            # has been reconciled to the complete 016 schema.
            cur.execute(
                "CREATE TABLE public.alembic_version (version_num VARCHAR(32) NOT NULL)"
            )
            cur.execute(
                "ALTER TABLE ONLY public.alembic_version "
                "ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)"
            )
            cur.execute(
                "INSERT INTO public.alembic_version (version_num) "
                "VALUES ('016_m02_identity_intelligence')"
            )

        conn.commit()
        print("Legacy CareerOS M02 database reconciled and stamped at 016_m02_identity_intelligence.")
        return 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
