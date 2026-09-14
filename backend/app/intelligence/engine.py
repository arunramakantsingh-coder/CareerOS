from __future__ import annotations

"""Compatibility entrypoint for the CareerOS Global Intelligence Engine.

All application callers historically import ``engine`` from this module.
Keep that contract stable while making the health-gated, task-aware routed
runtime the single execution path.
"""

from app.intelligence.engine_runtime import RoutedIntelligenceEngine, routed_engine

# Preserve the historical class name for callers that import it directly.
IntelligenceEngine = RoutedIntelligenceEngine

# Preserve the historical module-level singleton while routing every request
# through the Global Intelligence Engine runtime.
engine = routed_engine
