from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.document import Document
from app.schemas.candidate import DocumentResponse, DocumentUploadRequest
from app.utils.document_processing import STORAGE_ROOT, extract_zip, save_document, sha256_bytes, safe_filename, is_supported
from app.utils.extraction_service import ExtractionService

router = APIRouter(prefix='/documents', tags=['documents'])
extraction_service = ExtractionService()


def get_or_create_profile(current_user: User, db: Session):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id, CandidateProfile.is_active == True).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id, full_name=current_user.name, primary_email=current_user.email, reconciliation_status='pending')
        db.add(profile); db.commit(); db.refresh(profile)
    return profile


def classify(name: str, mime: str | None = None) -> tuple[str, str | None]:
    lower = name.lower()
    if any(x in lower for x in ('resume', 'cv')): return 'cv', 'resume'
    if any(x in lower for x in ('offer', 'appointment', 'joining')): return 'employment', 'offer_letter'
    if any(x in lower for x in ('experience', 'relieving', 'employment')): return 'employment', 'experience_letter'
    if any(x in lower for x in ('certificate', 'certification', 'credential', 'ccna', 'ccnp', 'ccie', 'cissp', 'aws', 'azure')): return 'certification', 'certificate'
    if any(x in lower for x in ('degree', 'diploma', 'transcript', 'marksheet', 'mark-sheet')): return 'education', 'degree'
    if any(x in lower for x in ('project', 'portfolio')): return 'project', None
    if any(x in lower for x in ('award', 'achievement', 'appreciation')): return 'achievement', None
    return 'other', None


def create_record(profile, name: str, content: bytes, db: Session, category: Optional[str] = None, subcategory: Optional[str] = None, source: str = 'upload', source_metadata: Optional[dict] = None):
    digest = sha256_bytes(content)
    existing = db.query(Document).filter(Document.candidate_id == profile.id).all()
    duplicate_of = None
    for item in existing:
        if (item.source_metadata or {}).get('sha256') == digest:
            duplicate_of = str(item.id); break

    stored_path, _ = save_document(str(profile.id), name, content)
    inferred_category, inferred_subcategory = classify(name)
    document = Document(
        candidate_id=profile.id,
        filename=Path(stored_path).name,
        original_filename=name,
        file_size=len(content),
        file_type=Path(name).suffix.lower().lstrip('.') or None,
        mime_type=None,
        storage_path=stored_path,
        storage_url=f'/api/v1/documents/download/{profile.id}/{Path(stored_path).name}',
        document_category=category or inferred_category,
        document_subcategory=subcategory or inferred_subcategory,
        document_type=inferred_subcategory,
        status='processing',
        processing_status={'stage': 'uploaded', 'duplicate_of': duplicate_of},
        extraction_status='pending',
        source=source,
        source_metadata={**(source_metadata or {}), 'sha256': digest, 'original_path': name},
    )
    db.add(document); db.commit(); db.refresh(document)
    if duplicate_of:
        document.processing_status = {'stage': 'duplicate', 'duplicate_of': duplicate_of}
        document.status = 'processed'; document.extraction_status = 'complete'; db.commit(); db.refresh(document)
        return document
    try:
        document.processing_status = {'stage': 'extracting'}; db.commit()
        extraction_service.extract_from_document(document, db)
    except Exception as exc:
        document.status = 'failed'; document.extraction_status = 'failed'; document.processing_status = {'stage': 'failed', 'error': str(exc)[:500]}; db.commit(); db.refresh(document)
    return document


@router.post('/upload', response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), document_category: Optional[str] = Form(None), document_subcategory: Optional[str] = Form(None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_or_create_profile(current_user, db)
    content = await file.read()
    if not is_supported(file.filename or ''):
        raise HTTPException(400, 'Unsupported document format')
    return create_record(profile, file.filename or 'document', content, db, document_category, document_subcategory)


@router.post('/bulk-upload')
async def bulk_upload(files: List[UploadFile] = File(...), document_category: Optional[str] = Form(None), document_subcategory: Optional[str] = Form(None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if len(files) > 100: raise HTTPException(400, 'Maximum 100 upload items per batch')
    profile = get_or_create_profile(current_user, db)
    created = []; rejected = []
    for upload in files:
        name = upload.filename or 'document'
        try:
            content = await upload.read()
            if Path(name).suffix.lower() == '.zip':
                archive = create_record(profile, name, content, db, 'other', 'archive', 'zip_upload')
                created.append(archive)
                for entry_name, entry_content in extract_zip(content):
                    created.append(create_record(profile, entry_name, entry_content, db, document_category, document_subcategory, 'zip_extract', {'zip_source': name}))
            elif is_supported(name):
                created.append(create_record(profile, name, content, db, document_category, document_subcategory, 'upload'))
            else:
                rejected.append({'filename': name, 'reason': 'Unsupported format'})
        except Exception as exc:
            rejected.append({'filename': name, 'reason': str(exc)[:300]})
    return {'created': len(created), 'documents': created, 'rejected': rejected}


@router.post('/upload-base64', response_model=DocumentResponse)
def upload_document_base64(request: DocumentUploadRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    import base64
    try: content = base64.b64decode(request.content)
    except Exception: raise HTTPException(400, 'Invalid base64 content')
    profile = get_or_create_profile(current_user, db)
    return create_record(profile, request.filename, content, db, request.document_category, request.document_subcategory, 'upload')


@router.get('/', response_model=List[DocumentResponse])
def get_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id, CandidateProfile.is_active == True).first()
    if not profile: return []
    return db.query(Document).filter(Document.candidate_id == profile.id).order_by(Document.created_at.desc()).all()


@router.get('/categories')
def get_document_categories():
    return {'categories': [{'value': 'cv', 'label': 'CV / Resume'}, {'value': 'employment', 'label': 'Employment Evidence'}, {'value': 'certification', 'label': 'Certification'}, {'value': 'education', 'label': 'Education'}, {'value': 'project', 'label': 'Project'}, {'value': 'achievement', 'label': 'Achievement'}, {'value': 'other', 'label': 'Other'}]}


@router.get('/download/{candidate_id}/{stored_filename}')
def download_document(candidate_id: uuid.UUID, stored_filename: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == candidate_id, CandidateProfile.user_id == current_user.id).first()
    if not profile: raise HTTPException(403, 'Not authorized')
    document = db.query(Document).filter(Document.candidate_id == candidate_id, Document.filename == stored_filename).first()
    if not document: raise HTTPException(404, 'Document not found')
    path = (STORAGE_ROOT / document.storage_path).resolve()
    if STORAGE_ROOT not in path.parents or not path.is_file(): raise HTTPException(404, 'Stored evidence not found')
    return FileResponse(path, media_type=document.mime_type or 'application/octet-stream', filename=document.original_filename)


@router.get('/{document_id}', response_model=DocumentResponse)
def get_document(document_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document: raise HTTPException(404, 'Document not found')
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == document.candidate_id, CandidateProfile.user_id == current_user.id).first()
    if not profile: raise HTTPException(403, 'Not authorized')
    return document


@router.delete('/{document_id}')
def delete_document(document_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document: raise HTTPException(404, 'Document not found')
    profile = db.query(CandidateProfile).filter(CandidateProfile.id == document.candidate_id, CandidateProfile.user_id == current_user.id).first()
    if not profile: raise HTTPException(403, 'Not authorized')
    db.delete(document); db.commit(); return {'message': 'Document deleted'}
