from types import SimpleNamespace

import app.core.migrations as migrations


class FakeInspector:
    def __init__(self, tables, columns):
        self._tables = set(tables)
        self._columns = columns

    def get_table_names(self):
        return list(self._tables)

    def get_columns(self, table):
        return [{"name": name} for name in self._columns.get(table, set())]


class FakeConnection:
    def __init__(self):
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, statement, params=None):
        self.executed.append((str(statement), params))
        return None


M02_TABLES = {
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

DOCUMENT_015_COLUMNS = {
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
}


def test_detects_016_schema(monkeypatch):
    tables = M02_TABLES | {
        "users",
        "career_fact_evidence",
        "persona_suggestions",
        "email_connector_accounts",
    }
    columns = {"users": {"id", "email", "role"}, "documents": DOCUMENT_015_COLUMNS}
    monkeypatch.setattr(migrations, "inspect", lambda engine: FakeInspector(tables, columns))

    assert migrations._detect_legacy_baseline() == migrations.HEAD


def test_detects_015_schema(monkeypatch):
    columns = {"users": {"id", "email"}, "documents": DOCUMENT_015_COLUMNS}
    monkeypatch.setattr(migrations, "inspect", lambda engine: FakeInspector(M02_TABLES, columns))

    assert migrations._detect_legacy_baseline() == migrations.BASELINE_015


def test_detects_014_schema(monkeypatch):
    columns = {"users": {"id", "email"}, "documents": {"id", "candidate_id", "filename"}}
    monkeypatch.setattr(migrations, "inspect", lambda engine: FakeInspector(M02_TABLES, columns))

    assert migrations._detect_legacy_baseline() == migrations.BASELINE_014


def test_unknown_legacy_schema_fails_closed(monkeypatch):
    tables = {"users", "career_profiles"}
    columns = {"users": {"id", "email"}}
    monkeypatch.setattr(migrations, "inspect", lambda engine: FakeInspector(tables, columns))

    assert migrations._detect_legacy_baseline() is None


def test_empty_database_uses_upgrade_head(monkeypatch):
    calls = []
    monkeypatch.setattr(migrations, "engine", SimpleNamespace(connect=lambda: FakeConnection()))
    monkeypatch.setattr(migrations, "_has_version_table", lambda: False)
    monkeypatch.setattr(migrations, "inspect", lambda engine: FakeInspector(set(), {}))
    monkeypatch.setattr(migrations, "_alembic_config", lambda: SimpleNamespace())
    monkeypatch.setattr(migrations.command, "upgrade", lambda cfg, revision: calls.append(("upgrade", revision)))

    migrations.reconcile_database()

    assert calls == [("upgrade", "head")]


def test_normalizes_legacy_017_without_rerunning_schema_migration(monkeypatch):
    connection = FakeConnection()
    monkeypatch.setattr(migrations, "engine", SimpleNamespace(
        connect=lambda: connection,
        begin=lambda: connection,
    ))
    monkeypatch.setattr(
        migrations,
        "_get_version_rows",
        lambda: ["017_m02_employment_semantic", "018_m02_profile_sections"],
    )
    monkeypatch.setattr(
        migrations,
        "_has_columns",
        lambda table, columns: table == "professional_experiences" and columns == migrations.EMPLOYMENT_SEMANTIC_COLUMNS,
    )

    class Revision:
        def __init__(self, down_revision):
            self.down_revision = down_revision

    class FakeScript:
        revisions = {
            "017_m02_employment_semantic_fields": Revision("016_m02_identity_intelligence"),
            "018_m02_profile_sections": Revision("017_m02_employment_semantic_fields"),
        }

        def get_revision(self, revision):
            return self.revisions.get(revision)

    monkeypatch.setattr(migrations.ScriptDirectory, "from_config", lambda cfg: FakeScript())

    migrations._normalize_legacy_revision_state(SimpleNamespace())

    statements = [statement for statement, _ in connection.executed]
    assert any("DELETE FROM alembic_version" in statement for statement in statements)
    assert any(
        "INSERT INTO alembic_version" in statement and params == {"revision": "018_m02_profile_sections"}
        for statement, params in connection.executed
    )
    assert not any(
        params == {"revision": "017_m02_employment_semantic_fields"}
        for _, params in connection.executed
    )
