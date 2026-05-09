from __future__ import annotations

from fastapi import HTTPException, status

from app.schemas.auth import CurrentUserResponse
from app.schemas.utilizador import PerfilUtilizador


def check_loja_access(loja_id: int, current_user: CurrentUserResponse) -> None:
    """Raises 403 LOJA_MISMATCH if a non-admin user tries to access data from another shop."""
    if current_user.perfil == PerfilUtilizador.ADMINISTRADOR:
        return
    if loja_id != current_user.loja_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "detail": "Acesso a dados de outra loja não permitido.",
                "code": "LOJA_MISMATCH",
            },
        )
