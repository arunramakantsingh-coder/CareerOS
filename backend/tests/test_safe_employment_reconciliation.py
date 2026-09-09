from types import SimpleNamespace
from uuid import uuid4
import inspect

# Import all relationship targets needed to configure the shared SQLAlchemy mapper
# registry when this focused test suite instantiates ProfessionalExperience.
import app.models.external_identity  # noqa: F401

from app.intelligence import safe_employment_reconciliation as safe
from app.models.professional_experience import ProfessionalExperience


def _document():
    return SimpleNamespace(id=uuid4(), candidate_id=uuid4())


def _experience(**overrides):
    value = {
        "organization": "CBI Bank",
        "client": None,
        "title": "Senior Manager – Network & Telecommunication",
        "start_date": "2018-08-01",
        "end_date": "2020-03-01",
        "is_current": False,
        "responsibilities": ["Network leadership"],
        "achievements": ["Improved resilience"],
        "technologies": ["Cisco"],
        "industries": ["Banking"],
        "confidence": 0.96,
        "evidence_excerpt": "CBI Bank role evidence",
    }
    value.update(overrides)
    return value


def test_mutable_lookup_is_scoped_to_document_and_ai_statuses(monkeypatch):
    document = _document()
    criteria = []

    class RecordingQuery:
        def filter(self, *args):
            criteria.extend(args)
            return self

        def all(self):
            return []

    db = SimpleNamespace(query=lambda model: RecordingQuery())
    monkeypatch.setattr(safe, "_best_match", lambda exp, rows, minimum: None)

    safe._find_mutable_experience_source_scoped(
        _experience(), document.candidate_id, document.id, db
    )

    keys = {criterion.left.key for criterion in criteria}
    assert keys == {"candidate_id", "source_id", "is_reconciled", "reconciliation_status"}
    assert any(criterion.left.key == "source_id" and criterion.right.value == document.id for criterion in criteria)
    assert any(criterion.left.key == "candidate_id" and criterion.right.value == document.candidate_id for criterion in criteria)
    is_reconciled_criterion = next(c for c in criteria if c.left.key == "is_reconciled")
    assert str(is_reconciled_criterion).endswith("IS false")
    status_criterion = next(c for c in criteria if c.left.key == "reconciliation_status")
    assert set(status_criterion.right.value) == {"extracted", "ai_reconciled", "ai_review"}


def test_apply_creates_new_source_owned_record_without_deleting(monkeypatch):
    document = _document()
    added = []
    db = SimpleNamespace(
        add=added.append,
        flush=lambda: None,
    )

    monkeypatch.setattr(safe, "_find_verified_match", lambda exp, candidate_id, db: None)
    monkeypatch.setattr(safe, "_find_mutable_experience_source_scoped", lambda exp, candidate_id, document_id, db: None)
    monkeypatch.setattr(safe, "_ensure_evidence", lambda *args, **kwargs: None)

    applied, review, protected = safe.apply_experiences_source_scoped(
        document, [_experience()], db
    )

    assert not review
    assert not protected
    assert len(applied) == 1
    assert len(added) == 1
    record = added[0]
    assert isinstance(record, ProfessionalExperience)
    assert record.candidate_id == document.candidate_id
    assert record.source_id == document.id
    assert record.source_type == "document"
    assert record.company == "CBI Bank"
    assert record.title == "Senior Manager – Network & Telecommunication"
    assert record.is_reconciled is True
    assert record.reconciliation_status == "ai_reconciled"


def test_apply_updates_only_same_document_mutable_record(monkeypatch):
    document = _document()
    target = ProfessionalExperience(
        id=uuid4(),
        candidate_id=document.candidate_id,
        company="CBI Bank",
        title="Senior Manager – Network & Telecommunication",
        source_id=document.id,
        source_type="document",
        is_reconciled=False,
        reconciliation_status="ai_review",
    )
    added = []
    db = SimpleNamespace(
        add=added.append,
        flush=lambda: None,
    )

    monkeypatch.setattr(safe, "_find_verified_match", lambda exp, candidate_id, db: None)
    monkeypatch.setattr(safe, "_find_mutable_experience_source_scoped", lambda exp, candidate_id, document_id, db: target)
    monkeypatch.setattr(safe, "_ensure_evidence", lambda *args, **kwargs: None)

    applied, review, protected = safe.apply_experiences_source_scoped(
        document,
        [_experience(confidence=0.91, technologies=["Cisco", "Palo Alto"])],
        db,
    )

    assert len(applied) == 1
    assert not review
    assert not protected
    assert added == []
    assert target.source_id == document.id
    assert target.technologies == ["Cisco", "Palo Alto"]
    assert target.is_reconciled is True
    assert target.reconciliation_status == "ai_reconciled"


def test_apply_protects_user_confirmed_record(monkeypatch):
    document = _document()
    verified = ProfessionalExperience(
        id=uuid4(),
        candidate_id=document.candidate_id,
        company="CBI Bank",
        title="Senior Manager – Network & Telecommunication",
        source_id=uuid4(),
        source_type="document",
        is_reconciled=True,
        reconciliation_status="user_confirmed",
    )
    db = SimpleNamespace(flush=lambda: None)

    monkeypatch.setattr(safe, "_find_verified_match", lambda exp, candidate_id, db: verified)
    mutable_called = {"value": False}

    def unexpected_mutable(*args, **kwargs):
        mutable_called["value"] = True
        raise AssertionError("user-confirmed record must not enter mutable matching")

    monkeypatch.setattr(safe, "_find_mutable_experience_source_scoped", unexpected_mutable)
    monkeypatch.setattr(safe, "_ensure_evidence", lambda *args, **kwargs: None)

    applied, review, protected = safe.apply_experiences_source_scoped(
        document, [_experience()], db
    )

    assert not applied
    assert not review
    assert len(protected) == 1
    assert mutable_called["value"] is False
    assert verified.reconciliation_status == "user_confirmed"
    assert verified.is_reconciled is True


def test_safe_writer_contains_no_destructive_delete_path():
    implementation = inspect.getsource(safe.apply_experiences_source_scoped)
    assert "db.delete(" not in implementation
    assert ".delete(" not in implementation
