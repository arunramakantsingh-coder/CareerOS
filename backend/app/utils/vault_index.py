from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def update_master_index(
    *,
    storage_root: Path,
    profile_id: str,
    document_id: str,
    owner: str | None,
    original_filename: str,
    stored_filename: str,
    category: str,
    subtype: str,
    confidence: float | int | None,
    content_hash: str,
    storage_path: str,
    metadata_markdown_path: str,
    derived_pdf_path: str | None,
    source_metadata: Dict[str, Any],
) -> str:
    """Append a stable evidence entry to the profile-level CareerOS master index.

    The index is derived navigation metadata. The uploaded source file remains authoritative.
    """
    system_dir = storage_root / profile_id / "00_SYSTEM"
    system_dir.mkdir(parents=True, exist_ok=True)
    index_path = system_dir / "MASTER_INDEX.md"

    if index_path.exists():
        current = index_path.read_text(encoding="utf-8", errors="replace")
    else:
        current = (
            "# CareerOS Professional Document Vault — Master Index\n\n"
            f"Owner: {owner or 'Unknown'}\n\n"
            "> This file is a derived index. Original uploaded evidence remains authoritative.\n\n"
            "## Documents\n\n"
        )

    marker = f"<!-- document:{document_id} -->"
    if marker in current:
        return str(index_path)

    relative_path = source_metadata.get("relative_path") or original_filename
    block = [
        marker,
        f"### {stored_filename}",
        f"- Document ID: `{document_id}`",
        f"- Original: `{original_filename}`",
        f"- Category: **{category}** / **{subtype}**",
        f"- Classification confidence: `{confidence}`",
        f"- SHA-256: `{content_hash}`",
        f"- Source path: `{relative_path}`",
        f"- Evidence file: `{storage_path}`",
        f"- Metadata record: `{metadata_markdown_path}`",
    ]
    if derived_pdf_path:
        block.append(f"- Derived PDF: `{derived_pdf_path}`")
    block.extend(["", ""])

    index_path.write_text(current.rstrip() + "\n\n" + "\n".join(block), encoding="utf-8")
    return str(index_path)
