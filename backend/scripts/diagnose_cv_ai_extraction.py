"""Read-only diagnostic for inspecting the Global Intelligence CV extraction result."""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path
from uuid import UUID

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from app.core.database import SessionLocal
from app.intelligence.ai_cv_ingestion import SCHEMA, _parse
from app.intelligence.contracts import IntelligenceRequest
from app.intelligence.engine import engine

DOCUMENT_ID = UUID("d1307403-ae5b-41ad-b296-d007f910b10b")
AI_TIMEOUT_SECONDS = 180
TASK = """Extract only the employment history from the supplied CV for diagnostic purposes.
Rules:
- The CV is the source of truth. Never invent or infer facts.
- Extract every genuine employment role, including multiple roles at one employer.
- Preserve employer, optional client, title and dates.
- Do not turn skills, technologies, projects, certifications, education or generic phrases into jobs.
- Use an empty array only when the CV genuinely contains no employment history.
- Return JSON matching the supplied CareerOS CV extraction schema; leave all non-employment sections empty/defaulted."""


def _run_engine(request: IntelligenceRequest):
    async def run_with_timeout():
        return await asyncio.wait_for(engine.execute(request), timeout=AI_TIMEOUT_SECONDS)

    try:
        return asyncio.run(run_with_timeout())
    except RuntimeError as exc:
        if "asyncio.run() cannot be called" not in str(exc):
            raise
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(run_with_timeout())
        finally:
            loop.close()


def main() -> int:
    started = time.monotonic()
    print("[1/4] Loading existing CV record (read-only)...", flush=True)
    db = SessionLocal()
    try:
        from sqlalchemy import text as sql_text

        row = db.execute(
            sql_text(
                "SELECT id, original_filename, document_category, source_metadata "
                "FROM documents WHERE id = :id"
            ),
            {"id": str(DOCUMENT_ID)},
        ).mappings().first()
        if row is None:
            print("DOCUMENT NOT FOUND", flush=True)
            return 2

        metadata = row.get("source_metadata") or {}
        text = metadata.get("extracted_text", "") if isinstance(metadata, dict) else ""
        if not isinstance(text, str) or not text.strip():
            print("NO EXTRACTED TEXT", flush=True)
            return 2

        print(f"[2/4] Extracted text loaded: {len(text)} characters", flush=True)
        request = IntelligenceRequest(
            task=TASK,
            context={
                "document": {
                    "id": str(row["id"]),
                    "filename": row["original_filename"],
                    "category": row["document_category"],
                    "text": text[:100000],
                }
            },
            output_schema=SCHEMA,
            tools=[],
            temperature=0.0,
        )

        print(f"[3/4] Calling active AI provider (timeout {AI_TIMEOUT_SECONDS}s)...", flush=True)
        ai_started = time.monotonic()
        try:
            result = _run_engine(request)
        except asyncio.TimeoutError:
            elapsed = time.monotonic() - ai_started
            print(f"AI TIMEOUT after {elapsed:.1f}s", flush=True)
            return 3
        except Exception as exc:
            elapsed = time.monotonic() - ai_started
            print(f"AI ERROR after {elapsed:.1f}s: {type(exc).__name__}: {exc}", flush=True)
            return 1

        print(f"AI RESPONSE RECEIVED after {time.monotonic() - ai_started:.1f}s", flush=True)
        print("STATUS:", result.status)
        print("PROVIDER:", result.provider)
        print("MODEL:", result.model)
        print("TRACE_ID:", result.trace_id)

        if result.status != "completed":
            print("RESULT:", result.result)
            return 1

        print("[4/4] Parsing employment result (no persistence)...", flush=True)
        payload = _parse(result.result)
        experiences = payload.get("experiences")
        print("EXPERIENCES_TYPE:", type(experiences).__name__)
        print("EXPERIENCE_COUNT:", len(experiences) if isinstance(experiences, list) else "NOT_A_LIST")
        print("EXPERIENCES_JSON:")
        print(json.dumps(experiences, indent=2, ensure_ascii=False, default=str))
        print("TOP_LEVEL_KEYS:", sorted(payload.keys()))
        print(f"TOTAL_DIAGNOSTIC_TIME: {time.monotonic() - started:.1f}s")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
