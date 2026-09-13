from fastapi import Depends, HTTPException, status
from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User


def is_developer(user: User) -> bool:
    """Role-based developer access with a centralized local bootstrap path."""
    if getattr(user, "role", "user") in {"developer", "admin"}:
        return True
    configured = {x.strip().lower() for x in settings.DEVELOPER_EMAILS if x.strip()}
    if configured and (user.email or "").lower() in configured:
        return True
    # Local development intentionally exposes Developer Mode to the authenticated
    # developer workspace. Production remains restricted to developer/admin roles
    # or the explicit allow-list above.
    return settings.ENVIRONMENT.lower() == "development"


def require_developer(user: User = Depends(get_current_user)) -> User:
    if not is_developer(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Developer Mode is restricted to authorized developer accounts")
    return user
