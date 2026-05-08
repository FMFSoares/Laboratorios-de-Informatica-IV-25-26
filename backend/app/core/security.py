from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
import bcrypt as _bcrypt
from jose import JWTError, jwt

from app.config import settings

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={"detail": "Token inválido ou expirado.", "code": "TOKEN_EXPIRED"},
    headers={"WWW-Authenticate": "Bearer"},
)


# ── Password hashing ──────────────────────────────────────────────────────────
# passlib 1.7.4 é incompatível com bcrypt >= 5.x; usar bcrypt diretamente.


def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


# ── JWT ───────────────────────────────────────────────────────────────────────


def _build_token(payload: dict[str, Any], expire: datetime, token_type: str) -> str:
    data = payload.copy()
    data.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": token_type})
    return jwt.encode(data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(payload: dict[str, Any]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return _build_token(payload, expire, "access")


def create_refresh_token(payload: dict[str, Any]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    return _build_token(payload, expire, "refresh")


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        raise _CREDENTIALS_EXCEPTION

    if payload.get("type") != expected_type:
        raise _CREDENTIALS_EXCEPTION

    return payload
