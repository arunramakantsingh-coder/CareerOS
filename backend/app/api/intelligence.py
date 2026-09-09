from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.intelligence.contracts import IntelligenceRequest, RetrievalRequest
from app.intelligence.engine import engine
from app.intelligence.registry import registry
from app.intelligence.retrieval import retrieve_career_knowledge
from app.models.user import User

router = APIRouter(prefix="/intelligence", tags=["intelligence"])
INTELLIGENCE_BASE_URL = os.getenv("INTELLIGENCE_BASE_URL", "http://intelligence:8100").rstrip("/")
TIMEOUT = float(os.getenv("INTELLIGENCE_STATUS_TIMEOUT_SECONDS", "8"))


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=120000)
    system: str | None = None
    response_schema: dict[str, Any] | None = None
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


async def _call(path: str, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            if method == "POST":
                response = await client.post(f"{INTELLIGENCE_BASE_URL}{path}", json=payload or {})
            else:
                response = await client.get(f"{INTELLIGENCE_BASE_URL}{path}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"Intelligence Engine unavailable: {exc}") from exc


@router.get("/status")
async def status(_: User = Depends(get_current_user)):
    return await _call("/health")


@router.get("/capabilities")
async def capabilities(_: User = Depends(get_current_user)):
    return {**await _call("/v1/capabilities"), "tools": registry.list()}


@router.get("/tools")
async def tools(_: User = Depends(get_current_user)):
    return {"tools": registry.list()}


@router.post("/execute")
async def execute(request: IntelligenceRequest, _: User = Depends(get_current_user)):
    try:
        return await engine.execute(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/retrieve")
async def retrieve(
    request: RetrievalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return tenant-scoped CareerOS knowledge with evidence references."""
    return retrieve_career_knowledge(
        db=db,
        user_id=current_user.id,
        query=request.query,
        top_k=request.top_k,
        filters=request.filters,
    )


@router.post("/generate")
async def generate(request: GenerateRequest, _: User = Depends(get_current_user)):
    return await _call(
        "/v1/generate",
        method="POST",
        payload=request.model_dump(exclude_none=True),
    )
