from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
import base64
import json
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.document import Document
from app.models.extraction_result import ExtractionResult
from app.schemas.candidate import DocumentResponse, DocumentUploadRequest

router = APIRouter(prefix="/documents", tags=["documents"])


# ============================================
# DOCUMENT UPLOAD
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
    file_size = len(content)
    
    # Create storage path (in a real implementation, this would be cloud storage)
    storage_path = f"documents/{profile.id}/{file.filename}"
    storage_url = f"/api/v1/documents/download/{profile.id}/{file.filename}"
    
    # Create document record
    document = Document(
        candidate_id=profile.id,
        filename=file.filename,
        original_filename=file.filename,
        file_size=file_size,
        file_type=file.filename.split(".")[-1] if "." in file.filename else None,
        mime_type=file.content_type,
        storage_path=storage_path,
        storage_url=storage_url,
        document_category=document_category or "cv",
        document_subcategory=document_subcategory,
        status="uploaded",
        extraction_status="pending"
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Trigger extraction (asynchronously in production)
    # For now, mark as processed
    document.status = "processed"
    document.extraction_status = "complete"
    db.commit()
    db.refresh(document)
    
    return document


@router.post("/upload-base64", response_model=DocumentResponse)
def upload_document_base64(
    request: DocumentUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document using base64 encoding."""
    
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
    
    # Decode base64 content
    try:
        content = base64.b64decode(request.content)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid base64 content"
        )
    
    file_size = len(content)
    storage_path = f"documents/{profile.id}/{request.filename}"
    storage_url = f"/api/v1/documents/download/{profile.id}/{request.filename}"
    
    # Create document record
    document = Document(
        candidate_id=profile.id,
        filename=request.filename,
        original_filename=request.filename,
        file_size=file_size,
        file_type=request.filename.split(".")[-1] if "." in request.filename else None,
        storage_path=storage_path,
        storage_url=storage_url,
        document_category=request.document_category or "cv",
        document_subcategory=request.document_subcategory,
        status="processed",
        extraction_status="complete"
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document


# ============================================
# DOCUMENT RETRIEVAL
# ============================================

@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents for the current user."""
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id,
        CandidateProfile.is_active == True
    ).first()
    
    if not profile:
        return []
    
    documents = db.query(Document).filter(
        Document.candidate_id == profile.id
    ).order_by(Document.created_at.desc()).all()
    
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document."""
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Verify ownership
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.id == document.candidate_id,
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    return document


@router.delete("/{document_id}")
def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document."""
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Verify ownership
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.id == document.candidate_id,
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # In production, delete the file from storage
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted"}


# ============================================
# DOCUMENT CATEGORIES
# ============================================

@router.get("/categories")
def get_document_categories():
    """Get available document categories."""
    return {
        "categories": [
            {"value": "cv", "label": "CV / Resume"},
            {"value": "employment", "label": "Employment Evidence"},
            {"value": "certification", "label": "Certification"},
            {"value": "education", "label": "Education"},
            {"value": "project", "label": "Project"},
            {"value": "achievement", "label": "Achievement"},
            {"value": "other", "label": "Other"}
        ],
        "subcategories": {
            "employment": [
                {"value": "offer_letter", "label": "Offer Letter"},
                {"value": "experience_letter", "label": "Experience Letter"},
                {"value": "relieving_letter", "label": "Relieving Letter"},
                {"value": "payslip", "label": "Payslip"}
            ],
            "education": [
                {"value": "degree", "label": "Degree"},
                {"value": "college", "label": "College"},
                {"value": "school", "label": "School"}
            ]
        }
    }
