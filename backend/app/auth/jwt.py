from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import settings


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _build_payload(data: dict, expires_delta: timedelta, token_type: str) -> dict:
    payload = data.copy()
    payload.update({
        "exp": _now_utc() + expires_delta,
        "iat": _now_utc(),
        "type": token_type,
    })
    return payload


def create_access_token(data: dict) -> str:
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = _build_payload(data, expires, "access")
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = _build_payload(data, expires, "refresh")
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodes and validates a JWT. Raises JWTError on failure.
    Callers should convert JWTError to HTTPException 401.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def decode_refresh_token(token: str) -> dict:
    """Like decode_token but also asserts type == 'refresh'."""
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise JWTError("Not a refresh token")
    return payload
