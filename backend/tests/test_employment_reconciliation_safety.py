from types import SimpleNamespace
from uuid import uuid4

from app.intelligence.ai_cv_ingestion import _apply_employment


class EmptyQuery:
    def filter(self, *_args, **_kwargs):
        return self

    def all(self):
        return []


class FakeDB:
    def __init__(self):
        self.added = []

    def query(self, *_args, **_kwargs):
        return EmptyQuery()

    def add(self, item):
        self.added.append(item)

    def flush(self):
        if self.added:
            self.added[-1].id = self.added[-1].id or uuid4()


def test_empty_ai_employment_is_a_no_op():
    document = SimpleNamespace(id=uuid4())
    profile = SimpleNamespace(id=uuid4())
    db = FakeDB()
    assert _apply_employment(document, profile, [], db) == (0, 0)
    assert db.added == []


def test_separate_roles_at_same_employer_are_preserved():
    document = SimpleNamespace(id=uuid4())
    profile = SimpleNamespace(id=uuid4())
    db = FakeDB()
    incoming = [
        {"employer": "CBI Bank", "title": "Senior Architect", "start_date": "2016-07", "end_date": "2018-07", "responsibilities": [], "achievements": [], "technologies": []},
        {"employer": "CBI Bank", "title": "Senior Manager", "start_date": "2018-08", "end_date": "2020-03", "responsibilities": [], "achievements": [], "technologies": []},
    ]
    applied, review = _apply_employment(document, profile, incoming, db)
    assert applied == 2
    assert review == 0
    assert len(db.added) == 2
    assert [row.title for row in db.added] == ["Senior Architect", "Senior Manager"]
