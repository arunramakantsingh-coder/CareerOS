from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


TrustState = Literal["EXTRACTED", "INFERRED", "USER-CONFIRMED", "CONFLICTING", "MISSING"]
FindingType = Literal["source_fact", "extracted_fact", "ai_inference", "recommendation"]


class EvidenceRef(BaseModel):
    document_id: UUID | None = None
    fact_type: str | None = None
    fact_id: UUID | None = None
    source_location: str | None = None
    excerpt: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    trust_state: TrustState | None = None


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=1, max_length=12000)
    top_k: int = Field(default=8, ge=1, le=50)
    filters: dict[str, Any] = Field(default_factory=dict)


class IntelligenceRequest(BaseModel):
    task: str = Field(min_length=1, max_length=12000)
    context: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] | None = None
    tools: list[str] = Field(default_factory=list, max_length=20)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


class IntelligenceFinding(BaseModel):
    finding_type: FindingType
    title: str
    content: Any
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: list[EvidenceRef] = Field(default_factory=list)


class IntelligenceResult(BaseModel):
    engine_version: str
    task: str
    status: Literal["completed", "needs_review", "failed"]
    result: Any = None
    findings: list[IntelligenceFinding] = Field(default_factory=list)
    evidence: list[EvidenceRef] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    model: str | None = None
    provider: str | None = None
    trace_id: UUID | None = None
