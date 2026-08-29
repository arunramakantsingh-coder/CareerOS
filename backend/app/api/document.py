from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
import base64
import json
import zipfile
import hashlib
import io
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.document import Document
from app.schemas.candidate import DocumentResponse, DocumentUploadRequest

router = APIRouter(prefix="/documents", tags=["documents"])

# Supported file types
SUPPORTED_MIME_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/jpeg",
    "image/png",
    "image/tiff",
    "text/plain"
]

SUPPORTED_EXTENSIONS = [".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".tiff", ".txt"]

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_ZIP_SIZE = 50 * 1024 * 1024   # 50 MB
MAX_ZIP_FILES = 50


# ============================================
# HELPER FUNCTIONS
# ============================================

def compute_hash(content: bytes) -> str:
    """Compute SHA-256 hash of content."""
    return hashlib.sha256(content).hexdigest()


def validate_file(content: bytes, filename: str) -> tuple[bool, str]:
    """Validate file content and type."""
    # Check size
    if len(content) > MAX_FILE_SIZE:
        return False, f"File exceeds {MAX_FILE_SIZE // 1024 // 1024} MB limit"
    
    # Check extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False, f"Unsupported file type: {ext}"
    
    return True, ""


def get_mime_type(filename: str) -> str:
    """Get MIME type from filename."""
    ext = os.path.splitext(filename)[1].lower()
    mime_map = {
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".tiff": "image/tiff",
        ".txt": "text/plain"
    }
    return mime_map.get(ext, "application/octet-stream")


def process_single_file(
    content: bytes,
    filename: str,
    candidate_id: uuid.UUID,
    db: Session,
    batch_id: Optional[uuid.UUID] = None,
    parent_zip_id: Optional[uuid.UUID] = None
) -> Document:
    """Process a single file and create document record."""
    
    # Validate
    valid, error = validate_file(content, filename)
    if not valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Compute hash
    content_hash = compute_hash(content)
    
    # Check for duplicate
    existing = db.query(Document).filter(
        Document.candidate_id == candidate_id,
        Document.content_hash == content_hash
    ).first()
    
    if existing:
        # Return existing document (soft duplicate)
        return existing
    
    # Create storage path
    file_ext = os.path.splitext(filename)[1]
    storage_filename = f"{uuid.uuid4()}{file_ext}"
    storage_path = f"documents/{candidate_id}/{storage_filename}"
    storage_url = f"/api/v1/documents/download/{candidate_id}/{storage_filename}"
    
    # Create document record
    document = Document(
        candidate_id=candidate_id,
        original_filename=filename,
        filename=storage_filename,
        file_size=len(content),
        file_type=file_ext[1:] if file_ext else None,
        mime_type=get_mime_type(filename),
        content_hash=content_hash,
        storage_path=storage_path,
        storage_url=storage_url,
        status="uploaded",
        extraction_status="pending",
        batch_id=batch_id,
        is_zip_content=parent_zip_id is not None,
        parent_zip_id=parent_zip_id,
        source="upload"
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # In production, store the file in cloud storage
    # For now, just return the document record
    
    return document


def process_zip(
    content: bytes,
    filename: str,
    candidate_id: uuid.UUID,
    db: Session,
    batch_id: uuid.UUID
) -> List[Document]:
    """Process a ZIP file and extract its contents."""
    
    documents = []
    
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
            # Validate ZIP
            file_list = zip_file.namelist()
            
            # Check file count
            if len(file_list) > MAX_ZIP_FILES:
                raise HTTPException(
                    status_code=400,
                    detail=f"ZIP contains too many files ({len(file_list)} > {MAX_ZIP_FILES})"
                )
            
            # Check total size
            total_size = sum(info.file_size for info in zip_file.infolist() if not info.is_dir())
            if total_size > MAX_ZIP_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"ZIP total size exceeds {MAX_ZIP_SIZE // 1024 // 1024} MB limit"
                )
            
            # Create document for the ZIP itself
            zip_doc = Document(
                candidate_id=candidate_id,
                original_filename=filename,
                filename=filename,
                file_size=len(content),
                file_type="zip",
                mime_type="application/zip",
                content_hash=compute_hash(content),
                storage_path=f"documents/{candidate_id}/{filename}",
                storage_url=f"/api/v1/documents/download/{candidate_id}/{filename}",
                status="processed",
                extraction_status="complete",
                batch_id=batch_id,
                source="upload"
            )
            db.add(zip_doc)
            db.commit()
            db.refresh(zip_doc)
            
            # Process each file in ZIP
            for file_info in zip_file.infolist():
                if file_info.is_dir():
                    continue
                
                # Security: prevent path traversal
                if file_info.filename.startswith(("..", "/", "\\")):
                    continue
                
                try:
                    file_content = zip_file.read(file_info.filename)
                    doc = process_single_file(
                        file_content,
                        os.path.basename(file_info.filename),
                        candidate_id,
                        db,
                        batch_id,
                        zip_doc.id
                    )
                    documents.append(doc)
                except Exception as e:
                    # Log error but continue processing other files
                    print(f"Error processing {file_info.filename}: {e}")
            
            return documents
            
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid or corrupted ZIP file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing ZIP: {str(e)}")


# ============================================
# API ENDPOINTS
# ============================================

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_category: Optional[str] = Form(None),
    document_subcategory: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document to the Professional Document Vault."""
    
    # Get or create profile
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        profile = CandidateProfile(
            user_id=current_user.id,
            full_name=current_user.name,
            primary_email=current_user.email,
            reconciliation_status="pending"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    # Read file content
    content = await file.read()
    
    # Handle ZIP files
    batch_id = uuid.uuid4()
    if file.filename.lower().endswith(".zip"):
        documents = process_zip(content, file.filename, profile.id, db, batch_id)
        if documents:
            return documents[0]  # Return first document
        else:
            raise HTTPException(status_code=400, detail="No valid files found in ZIP")
    
    # Process single file
    doc = process_single_file(content, file.filename, profile.id, db, batch_id)
    
    # Set category if provided
    if document_category:
        doc.document_category = document_category
    if document_subcategory:
        doc.document_subcategory = document_subcategory
    
    db.commit()
    db.refresh(doc)
    
    return doc


@router.post("/upload-multiple")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload multiple files to the Professional Document Vault."""
    
    # Get or create profile
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        profile = CandidateProfile(
            user_id=current_user.id,
            full_name=current_user.name,
            primary_email=current_user.email,
            reconciliation_status="pending"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    batch_id = uuid.uuid4()
    results = []
    errors = []
    
    for file in files:
        try:
            content = await file.read()
            
            # Check if it's a ZIP
            if file.filename.lower().endswith(".zip"):
                docs = process_zip(content, file.filename, profile.id, db, batch_id)
                for doc in docs:
                    results.append({
                        "filename": doc.original_filename,
                        "document_id": str(doc.id),
                        "status": "uploaded"
                    })
            else:
                doc = process_single_file(content, file.filename, profile.id, db, batch_id)
                results.append({
                    "filename": doc.original_filename,
                    "document_id": str(doc.id),
                    "status": "uploaded"
                })
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "results": results,
        "errors": errors,
        "total": len(results) + len(errors),
        "successful": len(results)
    }
