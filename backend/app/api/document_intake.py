from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.candidate_profile import CandidateProfile
from app.models.document import Document
from app.models.user import User
from app.utils.document_ingestion import (
    IMAGE_EXTENSIONS,
    MAX_FILE_SIZE,
    SUPPORTED_EXTENSIONS,
    build_markdown_record,
    canonical_filename,
    classify_document,
    extract_text,
    image_to_pdf,
    iter_zip_entries,
    safe_filename,
    safe_relative_path,
    sha256_bytes,
)
from app.utils.extraction_service import ExtractionService
from app.utils.vault_index import update_master_index

router = APIRouter(prefix="/documents", tags=["document-intake"])
extraction_service = ExtractionService()

STORAGE_ROOT = Path(os.getenv("CAREEROS_STORAGE_ROOT", "/app/storage/documents"))


def get_profile(current_user: User, db: Session) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True,
    ).first()
    if not profile:
        profile = CandidateProfile(
            user_id=current_user.id,
            full_name=current_user.name,
            primary_email=current_user.email,
            reconciliation_status="pending",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def parse_relative_paths(raw: Optional[str], file_count: int) -> list[Optional[str]]:
    """Accept the v1.4 JSON field while remaining tolerant of the older single-string client.

    FastAPI/Pydantic 2 does not reliably coerce a single multipart string into List[str], which caused
    the visible `Input should be a valid list` 422 response. A JSON array in one form field has a
    deterministic shape for single files, multiple files, folders and ZIP uploads.
    """
    if not raw:
        return [None] * file_count
    try:
        decoded = json.loads(raw)
        if isinstance(decoded, list):
            paths = [str(item) if item is not None else None for item in decoded]
        else:
            paths = [str(decoded)]
    except (json.JSONDecodeError, TypeError, ValueError):
        paths = [raw]
    if len(paths) < file_count:
        paths.extend([None] * (file_count - len(paths)))
    return paths[:file_count]


def persist_document(
    profile: CandidateProfile,
    filename: str,
    content: bytes,
    mime_type: Optional[str],
    db: Session,
    batch_id: uuid.UUID,
    relative_path: Optional[str] = None,
    is_zip_content: bool = False,
    parent_zip_id: Optional[uuid.UUID] = None,
) -> Document:
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"{filename}: file exceeds 25MB limit")

    original = safe_filename(filename)
    suffix = Path(original).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS and not is_zip_content:
        raise HTTPException(status_code=400, detail=f"Unsupported document type: {suffix or 'unknown'}")

    content_hash = sha256_bytes(content)
    duplicate = db.query(Document).filter(
        Document.candidate_id == profile.id,
        Document.content_hash == content_hash,
    ).first()

    text, extraction_meta = extract_text(original, mime_type, content)
    classification = classify_document(original, text)

    storage_dir = STORAGE_ROOT / str(profile.id) / str(batch_id)
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_path = storage_dir / original
    storage_path.write_bytes(content)

    issuer = None
    if text:
        for line in text.splitlines():
            lower = line.lower().strip()
            if lower.startswith("issuer:") or lower.startswith("issued by:"):
                issuer = line.split(":", 1)[1].strip()[:255]
                break

    filename_for_vault = canonical_filename(profile.full_name, classification, issuer, original)
    final_path = storage_dir / filename_for_vault
    if final_path != storage_path:
        final_path.write_bytes(content)
        storage_path.unlink(missing_ok=True)
        storage_path = final_path

    derived_pdf_path: Optional[Path] = None
    if suffix in IMAGE_EXTENSIONS:
        try:
            derived_pdf = image_to_pdf(content)
            derived_pdf_path = storage_dir / f"{Path(filename_for_vault).stem} - derived.pdf"
            derived_pdf_path.write_bytes(derived_pdf)
        except Exception as exc:
            extraction_meta = {**extraction_meta, "derived_pdf_error": str(exc)}

    source_metadata = {
        "relative_path": relative_path,
        "extraction": extraction_meta,
        "duplicate_of": str(duplicate.id) if duplicate else None,
        "original_authoritative": True,
        "derived_text_stored": True,
        "derived_pdf_path": str(derived_pdf_path) if derived_pdf_path else None,
        "ingestion_batch": str(batch_id),
        "extracted_text": text[:100000],
    }

    document = Document(
        candidate_id=profile.id,
        filename=filename_for_vault,
        original_filename=original,
        file_size=len(content),
        file_type=suffix.lstrip("."),
        mime_type=mime_type,
        storage_path=str(storage_path),
        storage_url=None,
        document_category=classification["category"],
        document_subcategory=classification["subcategory"],
        document_type=classification["subcategory"],
        status="duplicate" if duplicate else "processed",
        processing_status={
            "stage": "profile_enrichment_pending",
            "classification": classification,
            "extraction": extraction_meta,
        },
        extraction_status="pending" if text or extraction_meta.get("ocr_required") else "failed",
        source="upload",
        source_metadata=source_metadata,
        content_hash=content_hash,
        issuer=issuer,
        batch_id=batch_id,
        is_zip_content=is_zip_content,
        parent_zip_id=parent_zip_id,
        classification_confidence=classification["confidence"],
    )
    db.add(document)
    db.flush()

    metadata_path = storage_dir / f"{Path(filename_for_vault).stem}.metadata.md"
    metadata_path.write_text(
        build_markdown_record(
            document_id=str(document.id),
            owner=profile.full_name,
            original_filename=original,
            stored_filename=filename_for_vault,
            content_hash=content_hash,
            classification=classification,
            extraction_meta=extraction_meta,
            extracted_text=text,
            relative_path=relative_path,
            derived_pdf_path=str(derived_pdf_path) if derived_pdf_path else None,
        ),
        encoding="utf-8",
    )

    master_index_path = update_master_index(
        storage_root=STORAGE_ROOT,
        profile_id=str(profile.id),
        document_id=str(document.id),
        owner=profile.full_name,
        original_filename=original,
        stored_filename=filename_for_vault,
        category=classification["category"],
        subtype=classification["subcategory"],
        confidence=classification["confidence"],
        content_hash=content_hash,
        storage_path=str(storage_path),
        metadata_markdown_path=str(metadata_path),
        derived_pdf_path=str(derived_pdf_path) if derived_pdf_path else None,
        source_metadata=source_metadata,
    )

    document.source_metadata = {
        **source_metadata,
        "metadata_markdown_path": str(metadata_path),
        "master_index_path": master_index_path,
    }
    db.commit()
    db.refresh(document)

    if duplicate:
        document.processing_status = {
            **(document.processing_status or {}),
            "stage": "duplicate_review",
            "duplicate_of": str(duplicate.id),
        }
        db.commit()
        return document

    if text:
        try:
            extraction_service.extract_from_document(document, db)
        except Exception as exc:
            document.status = "failed"
            document.extraction_status = "failed"
            document.processing_status = {
                **(document.processing_status or {}),
                "stage": "extraction_failed",
                "error": str(exc),
            }
            db.commit()
    return document


@router.post("/batch-upload")
async def batch_upload(
    files: list[UploadFile] = File(...),
    relative_paths: Optional[str] = Form(None),
    document_category: Optional[str] = Form(None),
    document_subcategory: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bulk upload files, browser-selected folders, ZIP archives and scanner captures."""
    if not files:
        raise HTTPException(status_code=400, detail="No files supplied")
    if len(files) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 files per batch")

    profile = get_profile(current_user, db)
    batch_id = uuid.uuid4()
    results = []
    paths = parse_relative_paths(relative_paths, len(files))

    for index, upload in enumerate(files):
        content = await upload.read()
        original = safe_filename(upload.filename or "document")
        rel = safe_relative_path(paths[index])
        suffix = Path(original).suffix.lower()

        if suffix == ".zip" or upload.content_type in {"application/zip", "application/x-zip-compressed"}:
            zip_doc = persist_document(
                profile,
                original,
                content,
                upload.content_type,
                db,
                batch_id,
                relative_path=rel,
                is_zip_content=False,
            )
            try:
                extracted = []
                for entry_name, entry_content in iter_zip_entries(content):
                    child = persist_document(
                        profile,
                        entry_name,
                        entry_content,
                        None,
                        db,
                        batch_id,
                        relative_path=entry_name,
                        is_zip_content=True,
                        parent_zip_id=zip_doc.id,
                    )
                    extracted.append({
                        "id": str(child.id),
                        "filename": child.original_filename,
                        "status": child.status,
                        "category": child.document_category,
                        "extraction_status": child.extraction_status,
                    })
                zip_doc.processing_status = {
                    **(zip_doc.processing_status or {}),
                    "stage": "zip_extracted",
                    "children": extracted,
                }
                db.commit()
            except Exception as exc:
                zip_doc.status = "failed"
                zip_doc.processing_status = {
                    **(zip_doc.processing_status or {}),
                    "stage": "zip_failed",
                    "error": str(exc),
                }
                db.commit()
                raise HTTPException(status_code=400, detail=f"ZIP processing failed for {original}: {exc}")
            results.append({
                "id": str(zip_doc.id),
                "filename": zip_doc.original_filename,
                "status": zip_doc.status,
                "type": "zip",
                "children": extracted,
            })
            continue

        document = persist_document(
            profile,
            original,
            content,
            upload.content_type,
            db,
            batch_id,
            relative_path=rel,
        )
        if document_category:
            document.document_category = document_category
        if document_subcategory:
            document.document_subcategory = document_subcategory
        db.commit()
        results.append({
            "id": str(document.id),
            "filename": document.original_filename,
            "stored_filename": document.filename,
            "category": document.document_category,
            "confidence": document.classification_confidence,
            "status": document.status,
            "extraction_status": document.extraction_status,
            "metadata_markdown": (document.source_metadata or {}).get("metadata_markdown_path"),
            "master_index": (document.source_metadata or {}).get("master_index_path"),
            "derived_pdf": (document.source_metadata or {}).get("derived_pdf_path"),
        })

    return {
        "batch_id": str(batch_id),
        "profile_id": str(profile.id),
        "uploaded": len(results),
        "results": results,
    }
