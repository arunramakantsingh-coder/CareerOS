from types import SimpleNamespace
from uuid import uuid4

from app.intelligence.identity_reconciliation import _apply_experiences, _merge_ai_with_source_anchors


def _anchor(company="Example Corp", title="Senior Architect"):
    return {
        "organization": company,
        "client": None,
        "title": title,
        "start_date": "2024-01-01",
        "end_date": None,
        "is_current": True,
        "responsibilities": ["Source responsibility"],
        "achievements": [],
        "technologies": [],
        "industries": [],
        "confidence": 0.97,
        "evidence_excerpt": f"{title} | {company}",
    }


def test_empty_ai_result_is_replaced_by_source_anchor():
    merged = _merge_ai_with_source_anchors([], [_anchor()])
    assert len(merged) == 1
    assert merged[0]["organization"] == "Example Corp"
    assert merged[0]["title"] == "Senior Architect"
    assert merged[0]["start_date"] == "2024-01-01"


def test_partial_ai_result_preserves_all_source_anchors():
    anchors = [_anchor("Example Corp", "Senior Architect"), _anchor("Other Corp", "Network Architect")]
    ai = [dict(_anchor("Example Corp", "Senior Architect"), responsibilities=["AI enrichment"])]
    merged = _merge_ai_with_source_anchors(ai, anchors)
    assert len(merged) == 2
    assert {row["organization"] for row in merged} == {"Example Corp", "Other Corp"}
    assert merged[0]["responsibilities"] == ["AI enrichment"]
    assert merged[1]["responsibilities"] == ["Source responsibility"]


def test_empty_apply_is_a_no_op():
    document = SimpleNamespace(candidate_id=uuid4(), source_metadata={})

    class ExplodingDB:
        def query(self, *_args, **_kwargs):
            raise AssertionError("empty AI result must not query or mutate employment")

    assert _apply_experiences(document, [], ExplodingDB()) == ([], [], [], 0)


def test_user_confirmed_match_is_protected_before_mutable_query(monkeypatch):
    document = SimpleNamespace(candidate_id=uuid4(), source_metadata={})
    confirmed = SimpleNamespace(id=uuid4(), company="Example Corp", title="Senior Architect")

    monkeypatch.setattr(
        "app.intelligence.identity_reconciliation._find_verified_match",
        lambda exp, candidate_id, db: confirmed,
    )
    monkeypatch.setattr(
        "app.intelligence.identity_reconciliation._ensure_evidence",
        lambda *args, **kwargs: None,
    )

    class ExplodingDB:
        def query(self, *_args, **_kwargs):
            raise AssertionError("protected employment must not enter mutable reconciliation")

    applied, review, protected, mutations = _apply_experiences(document, [_anchor()], ExplodingDB())
    assert applied == []
    assert review == []
    assert len(protected) == 1
    assert protected[0]["experience_id"] == str(confirmed.id)
    assert mutations == 0


def test_user_confirmed_rows_are_excluded_from_mutable_match(monkeypatch):
    document = SimpleNamespace(id=uuid4(), candidate_id=uuid4(), source_metadata={})
    confirmed = SimpleNamespace(
        id=uuid4(),
        company="Example Corp",
        client=None,
        title="Senior Architect",
        start_date=None,
        end_date=None,
        is_current=True,
        responsibilities=[],
        achievements=[],
        technologies=[],
        industries=[],
        industry=None,
        source_type="document",
        source_id=None,
        is_reconciled=True,
        reconciliation_status="user_confirmed",
    )
    mutable = SimpleNamespace(
        id=uuid4(),
        company="Other Corp",
        client=None,
        title="Network Architect",
        start_date=None,
        end_date=None,
        is_current=False,
        responsibilities=[],
        achievements=[],
        technologies=[],
        industries=[],
        industry=None,
        source_type="document",
        source_id=None,
        is_reconciled=False,
        reconciliation_status="ai_review",
    )
    captured_rows = []

    class Query:
        def filter(self, *_args, **_kwargs):
            return self

        def all(self):
            return [confirmed, mutable]

    class FakeDB:
        def query(self, *_args, **_kwargs):
            return Query()

        def flush(self):
            pass

        def add(self, *_args, **_kwargs):
            raise AssertionError("test should match the mutable row rather than create a new row")

    monkeypatch.setattr(
        "app.intelligence.identity_reconciliation._find_verified_match",
        lambda exp, candidate_id, db: None,
    )
    monkeypatch.setattr(
        "app.intelligence.identity_reconciliation._ensure_evidence",
        lambda *args, **kwargs: None,
    )

    def capture_best_match(exp, rows, minimum):
        captured_rows.extend(rows)
        return mutable

    monkeypatch.setattr(
        "app.intelligence.identity_reconciliation._best_match",
        capture_best_match,
    )

    applied, review, protected, mutations = _apply_experiences(
        document,
        [_anchor("Other Corp", "Network Architect")],
        FakeDB(),
    )

    assert captured_rows == [mutable]
    assert confirmed not in captured_rows
    assert applied and applied[0]["experience_id"] == str(mutable.id)
    assert review == []
    assert protected == []
    assert mutations == 1
