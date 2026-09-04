from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password, get_current_user
from app.models.user import User
from app.models.tenant import Tenant
from app.models.external_identity import ExternalIdentity
from app.schemas.auth import (
    RegisterRequest, RegisterResponse,
    LoginRequest, TokenResponse,
    UserResponse, UserUpdateRequest,
    ExternalIdentityRequest, ExternalIdentityResponse,
    ConsentRequest, ConsentResponse,
    PasswordCredentialRequest, PasswordStatusResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])


# ============================================
# REGISTRATION
# ============================================

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    tenant = Tenant(name=request.tenant_name or "default", plan="free", status="active")
    db.add(tenant)
    db.flush()

    user = User(
        email=request.email,
        name=request.name,
        password_hash=get_password_hash(request.password),
        tenant_id=tenant.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return RegisterResponse(
        id=user.id,
        tenant_id=tenant.id,
        email=user.email,
        name=user.name,
        is_active=user.is_active
    )


# ============================================
# LOGIN
# ============================================

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login and receive access token."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id), "tenant_id": str(user.tenant_id)})
    return TokenResponse(access_token=access_token, token_type="bearer")


# ============================================
# PASSWORD CREDENTIALS
# ============================================

@router.get("/password/status", response_model=PasswordStatusResponse)
def password_status(current_user: User = Depends(get_current_user)):
    """Return whether the authenticated account has a local password."""
    return PasswordStatusResponse(has_password=bool(current_user.password_hash))


@router.post("/password", response_model=PasswordStatusResponse)
def set_or_change_password(
    request: PasswordCredentialRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set a password for an OAuth-only account or change an existing password."""
    if current_user.password_hash:
        if not request.current_password or not verify_password(request.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is required and must be correct"
            )

    current_user.password_hash = get_password_hash(request.new_password)
    db.commit()
    return PasswordStatusResponse(has_password=True)


# ============================================
# EXTERNAL IDENTITY (OAuth)
# ============================================

@router.post("/external", response_model=ExternalIdentityResponse)
def register_external_identity(
    request: ExternalIdentityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register an external identity (OAuth)."""
    existing = db.query(ExternalIdentity).filter(
        ExternalIdentity.provider == request.provider,
        ExternalIdentity.provider_user_id == request.provider_user_id,
        ExternalIdentity.user_id == current_user.id
    ).first()
    if existing:
        existing.provider_email = request.provider_email
        existing.access_token = request.access_token
        existing.refresh_token = request.refresh_token
        existing.provider_data = request.provider_data
        existing.scopes = request.scopes
        existing.last_used = datetime.now()
        db.commit()
        db.refresh(existing)
        return existing

    identity = ExternalIdentity(
        user_id=current_user.id,
        provider=request.provider,
        provider_user_id=request.provider_user_id,
        provider_email=request.provider_email,
        access_token=request.access_token,
        refresh_token=request.refresh_token,
        provider_data=request.provider_data,
        scopes=request.scopes,
        last_used=datetime.now()
    )
    db.add(identity)
    db.commit()
    db.refresh(identity)
    return identity


@router.get("/external", response_model=list[ExternalIdentityResponse])
def list_external_identities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List external identities for the current user."""
    return db.query(ExternalIdentity).filter(
        ExternalIdentity.user_id == current_user.id,
        ExternalIdentity.is_active == True
    ).all()


@router.delete("/external/{identity_id}")
def remove_external_identity(
    identity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an external identity."""
    identity = db.query(ExternalIdentity).filter(
        ExternalIdentity.id == identity_id,
        ExternalIdentity.user_id == current_user.id
    ).first()
    if not identity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="External identity not found")
    identity.is_active = False
    db.commit()
    return {"message": "External identity removed"}


# ============================================
# USER PROFILE
# ============================================

@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    if request.name is not None:
        current_user.name = request.name
    if request.locale is not None:
        current_user.locale = request.locale
    if request.timezone is not None:
        current_user.timezone = request.timezone
    db.commit()
    db.refresh(current_user)
    return current_user


# ============================================
# CONSENT
# ============================================

@router.post("/consent", response_model=ConsentResponse)
def set_consent(
    request: ConsentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set user consent flags."""
    current_user.consent_flags = str(request.consent_flags)
    db.commit()
    db.refresh(current_user)
    return ConsentResponse(
        consent_flags=request.consent_flags,
        consent_version=request.consent_version,
        consented_at=datetime.now()
    )


@router.get("/consent", response_model=ConsentResponse)
def get_consent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user consent."""
    consent_flags = {}
    if current_user.consent_flags:
        try:
            consent_flags = eval(current_user.consent_flags)
        except Exception:
            pass
    return ConsentResponse(
        consent_flags=consent_flags,
        consent_version="1.0",
        consented_at=datetime.now()
    )
