from __future__ import annotations

from datetime import datetime, timedelta
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, decode_token, get_current_user
from app.models.candidate_profile import CandidateProfile
from app.models.email_connector_account import EmailConnectorAccount
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
GMAIL_SCOPES = ["openid", "email", "profile", "https://www.googleapis.com/auth/gmail.readonly"]


def frontend_origin(request: Request) -> str:
    configured = [x.rstrip("/") for x in settings.ALLOWED_ORIGINS]
    origin = (request.headers.get("origin") or request.headers.get("referer") or "").rstrip("/")
    if origin:
        if origin in configured: return origin
        try:
            from urllib.parse import urlparse
            parsed = urlparse(origin)
            if parsed.hostname and parsed.port in (3000, None): return f"{parsed.scheme}://{parsed.hostname}:3000"
        except Exception: pass
    return settings.FRONTEND_BASE_URL.rstrip("/")


def callback_uri(request: Request, provider: str) -> str:
    """Return the OAuth callback registered with the provider.

    OAuth redirect URIs must be stable and match the Google/LinkedIn client configuration
    exactly. Do not derive them from the inbound Host header because localhost aliases,
    reverse proxies and forwarded hosts can otherwise create a different redirect_uri.
    """
    if provider == "google":
        return settings.GOOGLE_OAUTH_REDIRECT_URI.rstrip("/")
    if provider == "linkedin":
        return settings.LINKEDIN_OAUTH_REDIRECT_URI.rstrip("/")
    raise ValueError(f"Unsupported OAuth provider: {provider}")


def state_token(provider: str, action: str, request: Request, user_id: str | None = None) -> str:
    return create_access_token({"purpose":"oauth_state","provider":provider,"action":action,"user_id":user_id,"frontend":frontend_origin(request)}, expires_delta=timedelta(minutes=10))


def parse_state(state: str, provider: str) -> dict:
    payload = decode_token(state)
    if payload.get("purpose") != "oauth_state" or payload.get("provider") != provider: raise HTTPException(status_code=400, detail="Invalid OAuth state")
    return payload


def oauth_error(frontend: str, provider: str, message: str, destination: str = "login", code: str | None = None) -> RedirectResponse:
    path = "/settings" if destination == "settings" else "/login"
    detail = {"oauth":"error","provider":provider,"message":message[:200]}
    if code: detail["code"] = code
    return RedirectResponse(f"{frontend}{path}?{urlencode(detail)}")


def oauth_complete_redirect(token: str, frontend: str, provider: str) -> RedirectResponse:
    return RedirectResponse(f"{frontend}/oauth/callback#{urlencode({'access_token':token,'provider':provider})}")


def gmail_authorization_url(request: Request, user: User) -> str:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET: raise HTTPException(status_code=503, detail="Google OAuth is not configured")
    params={"client_id":settings.GOOGLE_CLIENT_ID,"redirect_uri":callback_uri(request,"google"),"response_type":"code","scope":" ".join(GMAIL_SCOPES),"access_type":"offline","include_granted_scopes":"true","prompt":"consent","state":state_token("google","gmail",request,str(user.id))}
    return f"{GOOGLE_AUTH}?{urlencode(params)}"


async def exchange_code(provider: str, code: str, redirect_uri: str) -> dict:
    data={"code":code,"client_id":settings.GOOGLE_CLIENT_ID if provider=="google" else settings.LINKEDIN_CLIENT_ID,"client_secret":settings.GOOGLE_CLIENT_SECRET if provider=="google" else settings.LINKEDIN_CLIENT_SECRET,"redirect_uri":redirect_uri,"grant_type":"authorization_code"}
    token_url=GOOGLE_TOKEN if provider=="google" else LINKEDIN_TOKEN
    async with httpx.AsyncClient(timeout=15) as client:
        response=await client.post(token_url,data=data,headers={"Accept":"application/json"})
        if response.status_code >= 400:
            try: detail=response.json()
            except Exception: detail={"error":"token_exchange_failed"}
            raise RuntimeError(f"token_exchange:{detail.get('error','unknown')}:{detail.get('error_description','')}")
        return response.json()


async def fetch_userinfo(provider: str, access_token: str) -> dict:
    endpoint=GOOGLE_USERINFO if provider=="google" else LINKEDIN_USERINFO
    async with httpx.AsyncClient(timeout=15) as client:
        response=await client.get(endpoint,headers={"Authorization":f"Bearer {access_token}"})
        response.raise_for_status(); return response.json()


def token_expiry(tokens: dict) -> datetime | None:
    try: return datetime.utcnow()+timedelta(seconds=int(tokens.get("expires_in",0))) if tokens.get("expires_in") else None
    except (TypeError,ValueError): return None


def upsert_identity(db: Session, user: User, provider: str, info: dict, tokens: dict, scopes: list[str]) -> ExternalIdentity:
    provider_user_id=str(info.get("sub") or info.get("id") or "")
    if not provider_user_id: raise HTTPException(status_code=400, detail=f"{provider} did not return a member identifier")
    identity=db.query(ExternalIdentity).filter(ExternalIdentity.provider==provider,ExternalIdentity.provider_user_id==provider_user_id).first()
    if identity and identity.user_id!=user.id: raise HTTPException(status_code=409, detail="This external account is already linked to another CareerOS account")
    if not identity: identity=ExternalIdentity(user_id=user.id,provider=provider,provider_user_id=provider_user_id); db.add(identity)
    identity.provider_email=info.get("email"); identity.access_token=tokens.get("access_token"); identity.refresh_token=tokens.get("refresh_token") or identity.refresh_token; identity.token_expires_at=token_expiry(tokens) or identity.token_expires_at; identity.provider_data=info; identity.scopes=scopes; identity.last_used=datetime.utcnow(); db.commit(); db.refresh(identity)
    return identity


def ensure_email_connector(db: Session, user: User, identity: ExternalIdentity, provider: str, scopes: list[str], capabilities: dict):
    account=db.query(EmailConnectorAccount).filter(EmailConnectorAccount.user_id==user.id,EmailConnectorAccount.provider==provider,EmailConnectorAccount.external_identity_id==identity.id).first()
    if not account: account=EmailConnectorAccount(user_id=user.id,provider=provider,external_identity_id=identity.id); db.add(account)
    account.email_address=identity.provider_email; account.status="connected"; account.auth_method="oauth2"; account.scopes=scopes; account.capabilities=capabilities; account.token_expires_at=identity.token_expires_at; account.last_sync_status="not_started"; db.commit()


def enrich_candidate_from_identity(db: Session, user: User, info: dict) -> None:
    profile=db.query(CandidateProfile).filter(CandidateProfile.user_id==user.id,CandidateProfile.is_active.is_(True)).first()
    if not profile: profile=CandidateProfile(user_id=user.id,full_name=user.name,primary_email=user.email,reconciliation_status="pending"); db.add(profile); db.flush()
    if info.get("name") and not profile.full_name: profile.full_name=info["name"]
    if info.get("email") and not profile.primary_email: profile.primary_email=info["email"]
    db.commit()


@router.get("/google/start")
async def google_start(request: Request):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET: return oauth_error(frontend_origin(request),"google","Google OAuth is not configured")
    params={"client_id":settings.GOOGLE_CLIENT_ID,"redirect_uri":callback_uri(request,"google"),"response_type":"code","scope":"openid profile email","access_type":"offline","include_granted_scopes":"true","prompt":"select_account","state":state_token("google","login",request)}
    return RedirectResponse(f"{GOOGLE_AUTH}?{urlencode(params)}")


@router.get("/google/gmail/start")
async def google_gmail_start(request: Request,current_user: User=Depends(get_current_user)):
    return RedirectResponse(gmail_authorization_url(request,current_user))


@router.post("/google/gmail/authorize-url")
async def google_gmail_authorize_url(request: Request,current_user: User=Depends(get_current_user)):
    return {"authorization_url":gmail_authorization_url(request,current_user),"scopes":GMAIL_SCOPES,"redirect_uri":callback_uri(request,"google")}


@router.get("/linkedin/start")
async def linkedin_start(request: Request):
    if not settings.LINKEDIN_CLIENT_ID or not settings.LINKEDIN_CLIENT_SECRET: return oauth_error(frontend_origin(request),"linkedin","LinkedIn OAuth is not configured")
    params={"client_id":settings.LINKEDIN_CLIENT_ID,"redirect_uri":callback_uri(request,"linkedin"),"response_type":"code","scope":"openid profile email","state":state_token("linkedin","login",request)}
    return RedirectResponse(f"{LINKEDIN_AUTH}?{urlencode(params)}")


@router.get("/google/callback")
async def google_callback(request: Request,code: str|None=None,state: str|None=None,error: str|None=None,db: Session=Depends(get_db)):
    if not state: return oauth_error(frontend_origin(request),"google","Missing OAuth state")
    payload=parse_state(state,"google"); frontend=payload.get("frontend") or frontend_origin(request); destination="settings" if payload.get("action")=="gmail" else "login"
    if error: return oauth_error(frontend,"google",error,destination,error)
    if not code: return oauth_error(frontend,"google","Missing authorization code",destination)
    try: tokens=await exchange_code("google",code,callback_uri(request,"google")); info=await fetch_userinfo("google",tokens["access_token"])
    except Exception as exc: return oauth_error(frontend,"google",f"Google authorization failed: {str(exc)}",destination,"google_authorization_failed")
    if payload.get("action")=="gmail":
        user=db.query(User).filter(User.id==payload.get("user_id"),User.is_active.is_(True)).first()
        if not user: return oauth_error(frontend,"google","CareerOS session expired; please sign in again","login","session_expired")
        identity=upsert_identity(db,user,"google",info,tokens,GMAIL_SCOPES)
        ensure_email_connector(db,user,identity,"gmail",GMAIL_SCOPES,{"read_messages":True,"read_threads":True,"search_messages":True,"send_message":False,"modify_messages":False})
        return RedirectResponse(f"{frontend}/settings?oauth=connected&provider=gmail")
    email=info.get("email")
    if not email: return oauth_error(frontend,"google","Google did not return an email address")
    user=db.query(User).filter(User.email==email).first()
    if not user:
        tenant=Tenant(name="default",plan="free",status="active"); db.add(tenant); db.flush(); user=User(email=email,name=info.get("name") or email.split("@")[0],tenant_id=tenant.id,is_active=True); db.add(user); db.flush()
    upsert_identity(db,user,"google",info,tokens,["openid","profile","email"]); enrich_candidate_from_identity(db,user,info); token=create_access_token({"sub":str(user.id),"tenant_id":str(user.tenant_id)}); return oauth_complete_redirect(token,frontend,"Google")


@router.get("/linkedin/callback")
async def linkedin_callback(request: Request,code: str|None=None,state: str|None=None,error: str|None=None,db: Session=Depends(get_db)):
    if not state: return oauth_error(frontend_origin(request),"linkedin","Missing OAuth state")
    payload=parse_state(state,"linkedin"); frontend=payload.get("frontend") or frontend_origin(request)
    if error: return oauth_error(frontend,"linkedin",error,"login",error)
    if not code: return oauth_error(frontend,"linkedin","Missing authorization code")
    try: tokens=await exchange_code("linkedin",code,callback_uri(request,"linkedin")); info=await fetch_userinfo("linkedin",tokens["access_token"])
    except Exception as exc: return oauth_error(frontend,"linkedin",f"LinkedIn authorization failed: {str(exc)}","login","linkedin_authorization_failed")
    email=info.get("email")
    if not email: return oauth_error(frontend,"linkedin","LinkedIn did not return an email address")
    user=db.query(User).filter(User.email==email).first()
    if not user:
        tenant=Tenant(name="default",plan="free",status="active"); db.add(tenant); db.flush(); user=User(email=email,name=info.get("name") or email.split("@")[0],tenant_id=tenant.id,is_active=True); db.add(user); db.flush()
    upsert_identity(db,user,"linkedin",info,tokens,["openid","profile","email"]); enrich_candidate_from_identity(db,user,info); token=create_access_token({"sub":str(user.id),"tenant_id":str(user.tenant_id)}); return oauth_complete_redirect(token,frontend,"LinkedIn")


@router.post("/linkedin/sync-profile")
async def linkedin_sync_profile(current_user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    identity=db.query(ExternalIdentity).filter(ExternalIdentity.user_id==current_user.id,ExternalIdentity.provider=="linkedin",ExternalIdentity.is_active.is_(True)).first()
    if not identity or not identity.access_token: raise HTTPException(status_code=404,detail="LinkedIn is not connected")
    try: info=await fetch_userinfo("linkedin",identity.access_token)
    except Exception as exc: raise HTTPException(status_code=502,detail=f"LinkedIn profile sync failed: {exc}")
    identity.provider_data=info; identity.last_used=datetime.utcnow(); enrich_candidate_from_identity(db,current_user,info); db.commit(); return {"provider":"linkedin","synced":True,"profile":info}


@router.get("/external")
async def external_connections(current_user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    identities=db.query(ExternalIdentity).filter(ExternalIdentity.user_id==current_user.id,ExternalIdentity.is_active.is_(True)).all()
    return [{"id":str(x.id),"provider":x.provider,"provider_email":x.provider_email,"scopes":x.scopes or [],"token_status":"present" if x.access_token else "missing","token_expires_at":x.token_expires_at,"last_used":x.last_used} for x in identities]
