from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories.loja_repository import MockLojaRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.loja import LojaResponse
from app.schemas.utilizador import PerfilUtilizador
from app.utils.permissions import check_loja_access

_repo = MockLojaRepository()


# ── Helpers for other services ────────────────────────────────────────────────

def get_nome(loja_id: int) -> str | None:
    return _repo.get_nome(loja_id)


def get_telefone(loja_id: int) -> str | None:
    return _repo.get_telefone(loja_id)


# ── Casos de uso ──────────────────────────────────────────────────────────────

def listar(page: int, page_size: int, current_user: CurrentUserResponse) -> PaginatedResponse[LojaResponse]:
    loja_id_filtro = None if current_user.perfil == PerfilUtilizador.ADMINISTRADOR else current_user.loja_id
    itens = _repo.list(loja_id_filtro)

    total = len(itens)
    pages = max(1, -(-total // page_size))
    start = (page - 1) * page_size

    return PaginatedResponse[LojaResponse](
        data=[LojaResponse(**l.__dict__) for l in itens[start : start + page_size]],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def obter(loja_id: int, current_user: CurrentUserResponse) -> DataResponse[LojaResponse]:
    loja = _repo.get_by_id(loja_id)
    if loja is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Loja não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )
    check_loja_access(loja_id, current_user)
    return DataResponse[LojaResponse](data=LojaResponse(**loja.__dict__))
