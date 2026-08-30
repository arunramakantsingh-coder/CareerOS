from __future__ import annotations

from datetime import datetime, timedelta
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, decode_token, get_current_user
from app.models.candidate_profile import CandidateProfile
from app.models.external_identity import ExternalIdentity
from app.models.tenant import Tenant
from app.models.user import User

router = APIRouter(prefix="/auth/oauth", tags=["oauth"])

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO = "https://www.googleapis.com/oauth2/v3/userinfo"
LINKEDIN_AUTH = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_USERINFO = "https://api.linkedin.com/v2/userinfo"


def frontend_origin(request: Request) -> str:
    configured = [x.rstrip("/") for x in settings.ALLOWED_ORIGINS]
    origin = (request.headers.get("origin") or request.headers.get("referer") or "").rstrip("/")
    if origin:
        if origin in configured:
            return origin
        try:
            from urllib.parse import urlparse
            parsed = urlparse(origin)
            if parsed.hostname and parsed.port in (3000, None):
                return f"{parsed.scheme}://{parsed.hostname}:3000"
        except Exception:
            pass
    return settings.FRONTEND_BASE_URL.rstrip("/")


def callback_uri(request: Request, provider: str) -> str:
    return f"{request.url.scheme}://{request.url.netloc}/api/v1/auth/oauth/{provider}/callback"


def state_token(provider: str, action: str, request: Request, user_id: str | None = None) -> str:
    return create_access_token(
        {"purpose": "oauth_state", "provider": provider, "action": action, "user_id": user_id, "frontend": frontend_origin(request)},
        expires_delta=timedelta(minutes=10),
    )


def parse_state(state: str, provider: str) -> dict:
    payload = decode_token(state)
    if payload.get("purpose") != "oauth_state" or payload.get("provider") != provider:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    return payload


def oauth_error(frontend: str, provider: str, message: str) -> RedirectResponse:
    params = urlencode({"oauth": "error", "provider": provider, "message": message[:200]})
    return RedirectResponse(f"{frontend}/settings?{params}")


def oauth_complete_html(token: str, frontend: str, provider: str) -> HTMLResponse:
    safe_frontend = frontend.replace("'", "%27")
    safe_token = token.replace("'", "%27")
    html = f"""<!doctype html><html><body><p>Completing {provider} sign-in…</p><script>
try {{ localStorage.setItem('access_token','{safe_token}'); }} catch(e) {{}}
window.location.replace('{safe_frontend}/');
</script></body></html>"""
    return HTMLResponse(html)


async def exchange_code(provider: str, code: str, redirect_uri: str) -> dict:
    if provider == "google":
        data = {"code": code, "client_id": settings.GOOGLE_CLIENT_ID, "client_secret": settings.GOOGLE_CLIENT_SECRET, "redirect_uri": redirect_uri, "grant_type": "authorization_code"}
        token_url = GOOGLE_TOKEN
    else:
        data = {"code": code, "client_id": settings.LINKEDIN_CLIENT_ID, "client_secret": settings.LINKEDIN_CLIENT_SECRET, "redirect_uri": redirect_uri, "grant_type": "authorization_code"}
        token_url = LINKEDIN_TOKEN
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(token_url, data=data, headers={"Accept": "application/json"})
        response.raise_for_status()
        return response.json()


async def fetch_userinfo(provider: str, access_token: str) -> dict:
    endpoint = GOOGLE_USERINFO if provider == "google" else LINKEDIN_USERINFO
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(endpoint, headers={"Authorization": f"Bearer {access_token}"})
        response.raise_for_status()
        return response.json()


def upsert_identity(db: Session, user: User, provider: str, info: dict, tokens: dict, scopes: list[str]) -> ExternalIdentity:
    provider_user_id = str(info.get("sub") or info.get("id") or "")
    if not provider_user_id:
        raise HTTPException(status_code=400, detail=f"{provider} did not return a member identifier")
    identity = db.query(ExternalIdentity).filter(
        ExternalIdentity.provider == provider,
        ExternalIdentity.provider_user_id == provider_user_id,
    ).first()
    if identity and identity.user_id != user.id:
        raise HTTPException(status_code=409, detail="This external account is already linked to another CareerOS account")
    if not identity:
        identity = ExternalIdentity(user_id=user.id, provider=provider, provider_user_id=provider_user_id)
        db.add(identity)
    identity.provider_email = info.get("email")
    identity.access_token = tokens.get("access_token")
    identity.refresh_token = tokens.get("refresh_token") or identity.refresh_token
    identity.provider_data = info
    identity.scopes = scopes
    identity.last_used = datetime.utcnow()
    db.commit()
    db.refresh(identity)
    return identity


def enrich_candidate_from_identity(db: Session, user: User, info: dict) -> None:
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == user.id,
        CandidateProfile.is_active == True,
    ).first()
    if not profile:
        profile = CandidateProfile(
            user_id=user.id,
            full_name=user.name,
            primary_email=user.email,
            reconciliation_status="pending",
        )
        db.add(profile)
        db.flush()
    if info.get("name") and not profile.full_name:
        profile.full_name = info["name"]
    if info.get("email") and not profile.primary_email:
        profile.primary_email = info["email"]
    db.commit()


@router.get("/google/start")
async def google_start(request: Request):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        return oauth_error(frontend_origin(request), "google", "Google OAuth is not configured")
    redirect_uri = callback_uri(request, "google")
    scopes = ["openid", "profile", "email"]
    params = {"client_id": settings.GOOGLE_CLIENT_ID, "redirect_uri": redirect_uri, "response_type": "code", "scope": " ".join(scopes), "access_type": "offline", "include_granted_scopes": "true", "prompt": "select_account", "state": state_token("google", "login", request)}
    return RedirectResponse(f"{GOOGLE_AUTH}?{urlencode(params)}")


@router.get("/google/gmail/start")
async def google_gmail_start(request: Request, current_user: User = Depends(get_current_user)):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        return oauth_error(frontend_origin(request), "google", "Google OAuth is not configured")
    redirect_uri = callback_uri(request, "google")
    scopes = ["openid", "email", "profile", "https://www.googleapis.com/auth/gmail.readonly"]
    params = {"client_id": settings.GOOGLE_CLIENT_ID, "redirect_uri": redirect_uri, "response_type": "code", "scope": " ".join(scopes), "access_type": "offline", "include_granted_scopes": "true", "prompt": "consent", "state": state_token("google", "gmail", request, str(current_user.id))}
    return RedirectResponse(f"{GOOGLE_AUTH}?{urlencode(params)}")


@router.get("/linkedin/start")
async def linkedin_start(request: Request):
    if not settings.LINKEDIN_CLIENT_ID or not settings.LINKEDIN_CLIENT_SECRET:
        return oauth_error(frontend_origin(request), "linkedin", "LinkedIn OAuth is not configured")
    redirect_uri = callback_uri(request, "linkedin")
    scopes = ["openid", "profile", "email"]
    params = {"client_id": settings.LINKEDIN_CLIENT_ID, "redirect_uri": redirect_uri, "response_type": "code", "scope": " ".join(scopes), "state": state_token("linkedin", "login", request)}
    return RedirectResponse(f"{LINKEDIN_AUTH}?{urlencode(params)}")


@router.get("/google/callback")
async def google_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None, db: Session = Depends(get_db)):
    if not state:
        return oauth_error(frontend_origin(request), "google", "Missing OAuth state")
    payload = parse_state(state, "google")
    frontend = payload.get("frontend") or frontend_origin(request)
    if error:
        return oauth_error(frontend, "google", error)
    if not code:
        return oauth_error(frontend, "google", "Missing authorization code")
    try:
        tokens = await exchange_code("google", code, callback_uri(request, "google"))
        info = await fetch_userinfo("google", tokens["access_token"])
    except Exception as exc:
        return oauth_error(frontend, "google", f"Google authorization failed: {exc}")

    if payload.get("action") == "gmail":
        user = db.query(User).filter(User.id == payload.get("user_id"), User.is_active == True).first()
        if not user:
            return oauth_error(frontend, "google", "CareerOS session expired; please sign in again")
        upsert_identity(db, user, "google", info, tokens, ["openid", "email", "profile", "https://www.googleapis.com/auth/gmail.readonly"])
        return RedirectResponse(f"{frontend}/settings?oauth=connected&provider=gmail")

    email = info.get("email")
    if not email:
        return oauth_error(frontend, "google", "Google did not return an email address")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        tenant = Tenant(name="default", plan="free", status="active")
        db.add(tenant)
        db.flush()
        user = User(email=email, name=info.get("name") or email.split("@")[0], tenant_id=tenant.id, is_active=True)
        db.add(user)
        db.flush()
    upsert_identity(db, user, "google", info, tokens, ["openid", "profile", "email"])
    enrich_candidate_from_identity(db, user, info)
    return oauth_complete_html(create_access_token({"sub": str(user.id), "tenant_id": str(user.tenant_id)}), frontend, "Google")


@router.get("/linkedin/callback")
async def linkedin_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None, db: Session = Depends(get_db)):
    if not state:
        return oauth_error(frontend_origin(request), "linkedin", "Missing OAuth state")
    payload = parse_state(state, "linkedin")
    frontend = payload.get("frontend") or frontend_origin(request)
    if error:
        return oauth_error(frontend, "linkedin", error)
    if not code:
        return oauth_error(frontend, "linkedin", "Missing authorization code")
    try:
        tokens = await exchange_code("linkedin", code, callback_uri(request, "linkedin"))
        info = await fetch_userinfo("linkedin", tokens["access_token"])
    except Exception as exc:
        return oauth_error(frontend, "linkedin", f"LinkedIn authorization failed: {exc}")

    email = info.get("email")
    if not email:
        return oauth_error(frontend, "linkedin", "LinkedIn did not return an email address")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        tenant = Tenant(name="default", plan="free", status="active")
        db.add(tenant)
        db.flush()
        user = User(email=email, name=info.get("name") or email.split("@")[0], tenant_id=tenant.id, is_active=True)
        db.add(user)
        db.flush()
    upsert_identity(db, user, "linkedin", info, tokens, ["openid", "profile", "email"])
    enrich_candidate_from_identity(db, user, info)
    return oauth_complete_html(create_access_token({"sub": str(user.id), "tenant_id": str(user.tenant_id)}), frontend, "LinkedIn")


@router.post("/linkedin/sync-profile")
async def linkedin_sync_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    identity = db.query(ExternalIdentity).filter(
        ExternalIdentity.user_id == current_user.id,
        ExternalIdentity.provider == "linkedin",
        ExternalIdentity.is_active == True,
    ).first()
    if not identity or not identity.access_token:
        raise HTTPException(status_code=404, detail="LinkedIn is not connected")
    try:
        info = await fetch_userinfo("linkedin", identity.access_token)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LinkedIn profile sync failed: {exc}")
    identity.provider_data = info
    identity.last_used = datetime.utcnow()
    enrich_candidate_from_identity(db, current_user, info)
    db.commit()
    return {"provider": "linkedin", "synced": True, "profile": info}
