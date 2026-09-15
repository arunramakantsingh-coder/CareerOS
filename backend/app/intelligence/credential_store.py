from __future__ import annotations

import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


def _key() -> bytes:
    configured = getattr(settings, "INTELLIGENCE_CREDENTIAL_ENCRYPTION_KEY", "") or ""
    source = configured or settings.AUTH_SECRET_KEY
    return hashlib.sha256(source.encode("utf-8")).digest()


def encrypt_secret(value: str) -> str:
    if not value:
        return ""
    nonce = os.urandom(12)
    ciphertext = AESGCM(_key()).encrypt(nonce, value.encode("utf-8"), None)
    return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")


def decrypt_secret(value: str | None) -> str:
    if not value:
        return ""
    raw = base64.urlsafe_b64decode(value.encode("ascii"))
    nonce, ciphertext = raw[:12], raw[12:]
    return AESGCM(_key()).decrypt(nonce, ciphertext, None).decode("utf-8")
