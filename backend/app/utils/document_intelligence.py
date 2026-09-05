"""Compatibility facade for CareerOS document intelligence.

The implementation lives in document_intelligence_v2 so every ingestion/reclassification path uses
one content-first classifier and one section segmentation implementation.
"""

from app.utils.document_intelligence_v2 import classify_document, normalize_section_heading, segment_sections

__all__ = ["classify_document", "normalize_section_heading", "segment_sections"]
