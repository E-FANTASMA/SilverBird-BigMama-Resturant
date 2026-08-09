import os
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import bcrypt as bcrypt_lib
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

os.environ.setdefault("PASSLIB_BUILTIN_BCRYPT", "enabled")

if not hasattr(bcrypt_lib, "__about__"):
    class _BcryptAbout:
        __version__ = getattr(bcrypt_lib, "__version__", "4.x")

    bcrypt_lib.__about__ = _BcryptAbout()

_original_hashpw = bcrypt_lib.hashpw


def _compat_hashpw(secret: bytes, salt: bytes) -> bytes:
    if len(secret) > 72:
        secret = secret[:72]
    return _original_hashpw(secret, salt)


bcrypt_lib.hashpw = _compat_hashpw

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: UUID | str, extra: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire, "type": "access", "jti": uuid4().hex}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: UUID | str, extra: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire, "type": "refresh", "jti": uuid4().hex}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_refresh_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid access token") from exc


def decode_refresh_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_refresh_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid refresh token") from exc
