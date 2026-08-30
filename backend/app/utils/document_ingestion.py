from __future__ import annotations

import hashlib
import io
import re
import subprocess
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

SUPPORTED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".rtf", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".zip"}
MAX_FILE_SIZE = 25 * 1024 * 1024
MAX_ARCHIVE_SIZE = 100 * 1024 * 1024
MAX_ARCHIVE_UNCOMPRESSED_SIZE = 250 * 1024 * 1024
MAX_ARCHIVE_FILES = 100


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def safe_filename(name: str) -> str:
    name = Path(name or "document").name
    name = re.sub(r"[^A-Za-z0-9._ -]+", "_", name).strip(" .")
    return name[:255] or "document"


def safe_relative_path(relative_path: str | None) -> str | None:
    if not relative_path:
        return None
    normalized = relative_path.replace("\\", "/").lstrip("/")
    parts = [p for p in normalized.split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts):
        raise ValueError("Unsafe relative path")
    return "/".join(safe_filename(p) for p in parts)


def extract_text(filename: str, mime_type: str | None, content: bytes) -> Tuple[str, Dict[str, Any]]:
    suffix = Path(filename).suffix.lower()
    meta: Dict[str, Any] = {"method": "none", "ocr_required": False, "page_count": None}
    if suffix == ".txt" or (mime_type or "").startswith("text/"):
        return content.decode("utf-8", errors="replace"), {**meta, "method": "text"}
    if suffix == ".doc":
        try:
            result = subprocess.run(["antiword", "-"], input=content, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15, check=True)
            return result.stdout.decode("utf-8", errors="replace"), {**meta, "method": "antiword"}
        except Exception as exc:
            return "", {**meta, "method": "antiword_error", "error": str(exc)}
    if suffix == ".docx":
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            return text, {**meta, "method": "docx"}
        except Exception as exc:
            return "", {**meta, "method": "docx_error", "error": str(exc)}
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(content))
            pages = [(page.extract_text() or "") for page in reader.pages]
            text = "\n\n".join(pages).strip()
            meta["page_count"] = len(reader.pages)
            if text:
                return text, {**meta, "method": "pdf_text"}
        except Exception as exc:
            meta["pdf_error"] = str(exc)
        try:
            import fitz
            from PIL import Image
            import pytesseract
            pdf = fitz.open(stream=content, filetype="pdf")
            pages: List[str] = []
            for page in pdf:
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                image = Image.open(io.BytesIO(pix.tobytes("png")))
                pages.append(pytesseract.image_to_string(image))
            meta["page_count"] = len(pdf)
            return "\n\n".join(pages).strip(), {**meta, "ocr_required": True, "method": "pdf_ocr"}
        except Exception as exc:
            return "", {**meta, "ocr_required": True, "method": "pdf_ocr_error", "error": str(exc)}
    if suffix in {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}:
        try:
            from PIL import Image
            import pytesseract
            image = Image.open(io.BytesIO(content))
            return pytesseract.image_to_string(image).strip(), {**meta, "method": "image_ocr", "ocr_required": True}
        except Exception as exc:
            return "", {**meta, "method": "image_ocr_error", "ocr_required": True, "error": str(exc)}
    return "", {**meta, "method": "unsupported"}


def classify_document(filename: str, text: str) -> Dict[str, Any]:
    haystack = f"{filename}\n{text}".lower()
    rules = [
        ("certification", "certificate", ["certification", "certificate", "credential id", "certified"]),
        ("education", "degree", ["degree", "university", "college", "transcript", "bachelor", "master", "bba", "mba"]),
        ("employment", "offer_letter", ["offer letter", "appointment letter", "employment offer"]),
        ("employment", "experience_letter", ["experience letter", "employment certificate", "worked with"]),
        ("employment", "relieving_letter", ["relieving letter", "relieved from"]),
        ("employment", "payslip", ["payslip", "salary slip", "pay slip", "gross salary"]),
        ("achievement", "award", ["award", "recognition", "employee of the month", "appreciation"]),
        ("project", "project", ["project summary", "project completion", "statement of work"]),
        ("cv", "resume", ["resume", "curriculum vitae", "professional summary", "work experience", "skills"]),
        ("identity", "identity", ["passport", "date of birth", "nationality", "driving licence", "driving license"]),
    ]
    for category, subtype, terms in rules:
        hits = sum(1 for term in terms if term in haystack)
        if hits:
            return {"category": category, "subcategory": subtype, "confidence": round(min(0.55 + hits * 0.12, 0.99), 2)}
    return {"category": "other", "subcategory": "unclassified", "confidence": 0.25}


def canonical_filename(owner: str | None, classification: Dict[str, Any], issuer: str | None, original: str) -> str:
    stem = Path(original).stem
    owner_part = re.sub(r"[^A-Za-z0-9 -]+", "", owner or "Professional").strip()
    category = classification.get("category", "document").replace("_", " ").title()
    subtype = classification.get("subcategory", "").replace("_", " ").title()
    issuer_part = re.sub(r"[^A-Za-z0-9 -]+", "", issuer or "").strip()
    pieces = [owner_part, subtype or category]
    if issuer_part:
        pieces.append(issuer_part)
    if stem and stem.lower() not in {"document", "scan", "img", "image"}:
        pieces.append(stem)
    suffix = Path(original).suffix.lower() or ".bin"
    return safe_filename(" - ".join(p for p in pieces if p))[:240] + suffix


def iter_zip_entries(content: bytes) -> Iterable[Tuple[str, bytes]]:
    if len(content) > MAX_ARCHIVE_SIZE:
        raise ValueError("ZIP archive exceeds the 100MB limit")
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        infos = [info for info in archive.infolist() if not info.is_dir()]
        if len(infos) > MAX_ARCHIVE_FILES:
            raise ValueError("ZIP archive exceeds the 100-file limit")
        total_uncompressed = sum(info.file_size for info in infos)
        if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_SIZE:
            raise ValueError("ZIP archive expands beyond the 250MB safety limit")
        for info in infos:
            relative = safe_relative_path(info.filename) or "document"
            suffix = Path(relative).suffix.lower()
            if suffix not in SUPPORTED_EXTENSIONS or suffix == ".zip":
                continue
            if info.file_size > MAX_FILE_SIZE:
                continue
            if any(part == ".." for part in Path(relative).parts):
                raise ValueError("Unsafe ZIP entry path")
            yield relative, archive.read(info)
