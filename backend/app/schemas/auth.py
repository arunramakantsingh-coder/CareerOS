from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


# ============================================
# REGISTRATION
# ============================================

class RegisterRequest(BaseModel):
    """Registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1)
    tenant_name: Optional[str] = "default"


class RegisterResponse(BaseModel):
    """Registration response."""
    id: UUID
    tenant_id: UUID
    email: str
    name: str
    is_active: bool


# ============================================
# LOGIN
# ============================================

class LoginRequest(BaseModel):
    """Login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = 3600


# ============================================
# EXTERNAL IDENTITY (OAuth)
# ============================================

class ExternalIdentityRequest(BaseModel):
    """External identity request."""
    provider: str
    provider_user_id: str
    provider_email: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    provider_data: Optional[Dict[str, Any]] = None
    scopes: Optional[list[str]] = None


class ExternalIdentityResponse(BaseModel):
    """External identity response."""
    id: UUID
    user_id: UUID
    provider: str
    provider_user_id: str
    provider_email: Optional[str]
    is_active: bool
    last_used: Optional[datetime]
    created_at: datetime


# ============================================
# USER
# ============================================

class UserResponse(BaseModel):
    """User response."""
    id: UUID
    email: str
    name: str
    is_active: bool
    locale: Optional[str]
    timezone: Optional[str]
    created_at: datetime


class UserUpdateRequest(BaseModel):
    """User update request."""
    name: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None


# ============================================
# CONSENT
# ============================================

class ConsentRequest(BaseModel):
    """Consent request."""
    consent_flags: Dict[str, bool]
    consent_version: Optional[str] = "1.0"


class ConsentResponse(BaseModel):
    """Consent response."""
    consent_flags: Dict[str, bool]
    consent_version: str
    consented_at: datetime


# ============================================
# PASSWORD CREDENTIALS
# ============================================

class PasswordStatusResponse(BaseModel):
    """Whether the authenticated account has a local password credential."""
    has_password: bool


class PasswordCredentialRequest(BaseModel):
    """Set or change the authenticated user's local password."""
    new_password: str = Field(..., min_length=8)
    current_password: Optional[str] = None


# ============================================
# PASSWORD RESET
# ============================================

class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """Password reset confirm request."""
    token: str
    new_password: str = Field(..., min_length=8)
