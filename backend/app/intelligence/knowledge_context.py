from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable


TRUST_STATES = {
    "EXTRACTED",
    "INFERRED",
    "USER-CONFIRMED",
    "CONFLICTING",
    "MISSING",
}


@dataclass(frozen=True)
class EvidenceReference:
    document_id: str
    fact_type: str | None = None
    fact_id: str | None = None
    excerpt: str | None = None
    confidence: float | None = None
    trust_state: str | None = None
    source_type: str | None = None
    section: str | None = None
    page: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class KnowledgeItem:
    kind: str
    key: str
    value: Any
    evidence: tuple[EvidenceReference, ...] = ()
    trust_state: str = "EXTRACTED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "key": self.key,
            "value": self.value,
            "trust_state": self.trust_state,
            "evidence": [item.to_dict() for item in self.evidence],
        }


def normalize_trust_state(value: str | None) -> str:
    candidate = (value or "EXTRACTED").upper().replace("_", "-")
    return candidate if candidate in TRUST_STATES else "EXTRACTED"


def flatten_knowledge(items: Iterable[KnowledgeItem]) -> list[dict[str, Any]]:
    return [item.to_dict() for item in items]
