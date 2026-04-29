from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.auth.jwt import decode_token
from app.schemas.auth import AuthUserInfo
from app.schemas.utilizador import PerfilUtilizador

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas ou token expirado.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthUserInfo:
    try:
        payload = decode_token(token)
    except JWTError:
        raise _CREDENTIALS_EXCEPTION

    if payload.get("type") != "access":
        raise _CREDENTIALS_EXCEPTION

    try:
        return AuthUserInfo(
            id=int(payload["sub"]),
            nome=payload["nome"],
            email=payload["email"],
            perfil=PerfilUtilizador(payload["perfil"]),
            loja_id=payload.get("loja_id"),
            loja_nome=payload.get("loja_nome"),
        )
    except (KeyError, ValueError):
        raise _CREDENTIALS_EXCEPTION


def require_roles(*roles: PerfilUtilizador) -> Callable:
    """
    Returns a FastAPI dependency that raises 403 if the current user's
    perfil is not in the given roles.

    Usage:
        @router.get("/...", dependencies=[Depends(require_roles(ADMINISTRADOR, GERENTE_LOJA))])
    """
    def _check(user: AuthUserInfo = Depends(get_current_user)) -> AuthUserInfo:
        if user.perfil not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Não tem permissão para aceder a este recurso.",
            )
        return user

    return _check


def require_same_loja_or_admin(
    loja_id: int,
    user: AuthUserInfo = Depends(get_current_user),
) -> AuthUserInfo:
    """
    Raises 403 if the user is not ADMINISTRADOR and their loja_id
    does not match the requested loja_id.
    Intended for use inside route handlers, not as a direct Depends.
    """
    if user.perfil == PerfilUtilizador.ADMINISTRADOR:
        return user
    if user.loja_id != loja_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não tem acesso a dados de outra loja.",
        )
    return user


# ── Convenience dependencies ─────────────────────────────────────────────────

def admin_only(user: AuthUserInfo = Depends(get_current_user)) -> AuthUserInfo:
    return require_roles(PerfilUtilizador.ADMINISTRADOR)(user)


def admin_or_gerente(user: AuthUserInfo = Depends(get_current_user)) -> AuthUserInfo:
    return require_roles(
        PerfilUtilizador.ADMINISTRADOR,
        PerfilUtilizador.GERENTE_LOJA,
    )(user)


def admin_gerente_or_rececionista(user: AuthUserInfo = Depends(get_current_user)) -> AuthUserInfo:
    return require_roles(
        PerfilUtilizador.ADMINISTRADOR,
        PerfilUtilizador.GERENTE_LOJA,
        PerfilUtilizador.RECECIONISTA,
    )(user)


def any_authenticated(user: AuthUserInfo = Depends(get_current_user)) -> AuthUserInfo:
    return user
