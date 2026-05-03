from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token
from app.schemas.auth import CurrentUserResponse
from app.schemas.utilizador import PerfilUtilizador

_bearer = HTTPBearer()


# ── Utilizador autenticado ────────────────────────────────────────────────────


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> CurrentUserResponse:
    """Valida o JWT de acesso e devolve o utilizador autenticado."""
    payload = decode_token(credentials.credentials, expected_type="access")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Token sem identificador de utilizador.", "code": "TOKEN_EXPIRED"},
        )

    return CurrentUserResponse(
        id=int(user_id),
        nome=payload["nome"],
        email=payload["email"],
        perfil=PerfilUtilizador(payload["perfil"]),
        loja_id=payload.get("loja_id"),
        loja_nome=payload.get("loja_nome"),
        ativo=payload.get("ativo", True),
    )


# ── RBAC ──────────────────────────────────────────────────────────────────────


def require_roles(*perfis: PerfilUtilizador):
    """Factory: devolve uma dependency que exige um dos perfis indicados."""

    def _check(
        current_user: CurrentUserResponse = Depends(get_current_user),
    ) -> CurrentUserResponse:
        if current_user.perfil not in perfis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"detail": "Sem permissão para esta operação.", "code": "PERMISSION_DENIED"},
            )
        return current_user

    return _check


# ── Contexto de loja ──────────────────────────────────────────────────────────


def get_loja_context(
    loja_id: int | None = None,
    current_user: CurrentUserResponse = Depends(get_current_user),
) -> int | None:
    """Devolve a loja_id efectiva.

    ADMINISTRADOR pode filtrar por qualquer loja ou ver tudo (None).
    Os restantes perfis ficam sempre restritos à sua própria loja_id.
    Tentar aceder a dados de outra loja devolve 403 LOJA_MISMATCH.
    """
    if current_user.perfil == PerfilUtilizador.ADMINISTRADOR:
        return loja_id

    if loja_id is not None and loja_id != current_user.loja_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "detail": "Acesso a dados de outra loja não permitido.",
                "code": "LOJA_MISMATCH",
            },
        )

    return current_user.loja_id
