from __future__ import annotations

from fastapi import Depends, HTTPException, status
from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User


def is_developer(user: User) -> bool:
    """Role-based developer access with an optional centralized bootstrap allow-list."""
    if getattr(user, "role", "user") in {"developer", "admin"}:
        return True
    configured = {x.strip().lower() for x in settings.DEVELOPER_EMAILS if x.strip()}
    return bool(configured and (user.email or "").lower() in configured)


def require_developer(user: User = Depends(get_current_user)) -> User:
    if not is_developer(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Developer Mode is restricted to authorized developer accounts")
    return user
