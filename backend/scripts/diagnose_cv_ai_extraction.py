"""Read-only diagnostic for inspecting the Global Intelligence CV extraction result.

This script deliberately does not persist profile or employment changes. It loads the
existing CV document, sends its extracted text through the current Intelligence Engine,
and prints the parsed employment section plus basic payload diagnostics.
"""
from __future__ import annotations

import asyncio
import json
import sys
from uuid import UUID

from app.core.database import SessionLocal
from app.intelligence.ai_cv_ingestion import SCHEMA, _parse
from app.intelligence.contracts import IntelligenceRequest
from app.intelligence.engine import engine
from app.models.document import Document

DOCUMENT_ID = UUID("d1307403-ae5b-41ad-b296-d007f910b10b")

TASK = """Extract only the employment history from the supplied CV for diagnostic purposes.
Rules:
- The CV is the source of truth. Never invent or infer facts.
- Extract every genuine employment role, including multiple roles at one employer.
- Preserve employer, optional client, title and dates.
- Do not turn skills, technologies, projects, certifications, education or generic phrases into jobs.
- Use an empty array only when the CV genuinely contains no employment history.
- Return JSON matching the supplied CareerOS CV extraction schema; leave all non-employment sections empty/defaulted."""


def main() -> int:
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == DOCUMENT_ID).first()
        if document is None:
            print("DOCUMENT NOT FOUND")
            return 2

        text = (document.source_metadata or {}).get("extracted_text", "")
        if not isinstance(text, str) or not text.strip():
            print("NO EXTRACTED TEXT")
            return 2

        request = IntelligenceRequest(
            task=TASK,
            context={
                "document": {
                    "id": str(document.id),
                    "filename": document.original_filename,
                    "category": document.document_category,
                    "text": text[:100000],
                }
            },
            output_schema=SCHEMA,
            tools=[],
            temperature=0.0,
        )

        result = asyncio.run(engine.execute(request))
        print("STATUS:", result.status)
        print("PROVIDER:", result.provider)
        print("MODEL:", result.model)
        print("TRACE_ID:", result.trace_id)

        if result.status != "completed":
            print("RESULT:", result.result)
            return 1

        payload = _parse(result.result)
        experiences = payload.get("experiences")
        print("EXPERIENCES_TYPE:", type(experiences).__name__)
        print("EXPERIENCE_COUNT:", len(experiences) if isinstance(experiences, list) else "NOT_A_LIST")
        print("EXPERIENCES_JSON:")
        print(json.dumps(experiences, indent=2, ensure_ascii=False, default=str))
        print("TOP_LEVEL_KEYS:", sorted(payload.keys()))
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
