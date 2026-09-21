from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class IntelligenceTool:
    name: str
    description: str
    read_only: bool = True


class ToolRegistry:
    """Explicit allow-list of CareerOS intelligence tools.

    Tools are metadata-only at this stage. Concrete implementations are registered
    by domain services so the Intelligence Engine never receives unrestricted DB access.
    """

    def __init__(self) -> None:
        self._tools: dict[str, IntelligenceTool] = {}

    def register(self, tool: IntelligenceTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Intelligence tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> IntelligenceTool | None:
        return self._tools.get(name)

    def list(self) -> list[dict[str, Any]]:
        return [
            {"name": tool.name, "description": tool.description, "read_only": tool.read_only}
            for tool in sorted(self._tools.values(), key=lambda item: item.name)
        ]

    def validate_requested(self, names: list[str]) -> list[IntelligenceTool]:
        unknown = [name for name in names if name not in self._tools]
        if unknown:
            raise ValueError(f"Unknown intelligence tools: {', '.join(unknown)}")
        return [self._tools[name] for name in names]


registry = ToolRegistry()
for _tool in (
    IntelligenceTool("career_vault_search", "Search authoritative professional facts and provenance."),
    IntelligenceTool("evidence_search", "Search supporting document evidence and extracted fields."),
    IntelligenceTool("document_lookup", "Retrieve metadata and representations for an owned document."),
    IntelligenceTool("profile_lookup", "Read the current Professional Identity profile."),
    IntelligenceTool("persona_lookup", "Read persona positioning derived from Career Vault facts."),
):
    registry.register(_tool)
