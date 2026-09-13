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


def test_user_confirmed_match_is_protected(monkeypatch):
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
    assert mutations == 0
