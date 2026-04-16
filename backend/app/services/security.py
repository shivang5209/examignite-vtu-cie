from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def hash_password(password: str, salt: str | None = None) -> str:
    chosen_salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), chosen_salt.encode("utf-8"), 150_000).hex()
    return f"{chosen_salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    if "$" not in password_hash:
        return False
    salt, expected_digest = password_hash.split("$", 1)
    provided = hash_password(password, salt=salt).split("$", 1)[1]
    return hmac.compare_digest(provided, expected_digest)


def create_access_token(user_id: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=settings.refresh_token_days)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, object]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
