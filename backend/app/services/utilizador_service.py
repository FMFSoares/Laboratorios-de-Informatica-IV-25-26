from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories.utilizador_repository import MockUtilizadorRepository
from app.repositories.loja_repository import MockLojaRepository
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.utilizador import UtilizadorCreate, UtilizadorResponse
from app.core.security import hash_password

_repo = MockUtilizadorRepository()
_loja_repo = MockLojaRepository()


def listar_utilizadores(page: int, page_size: int) -> PaginatedResponse[UtilizadorResponse]:
    itens, total = _repo.list(page, page_size)
    pages = max(1, -(-total // page_size))

    return PaginatedResponse[UtilizadorResponse](
        data=[UtilizadorResponse(**u.__dict__) for u in itens],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def criar_utilizador(body: UtilizadorCreate) -> DataResponse[UtilizadorResponse]:
    if _repo.exists_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Email já registado no sistema.", "code": "DUPLICATE_ENTRY"},
        )

    loja_nome = _loja_repo.get_nome(body.loja_id) if body.loja_id else None

    novo = _repo.create(
        nome=body.nome,
        email=body.email,
        password_hash=hash_password(body.password),
        perfil=body.perfil,
        loja_id=body.loja_id,
        loja_nome=loja_nome,
        ativo=body.ativo,
    )

    return DataResponse[UtilizadorResponse](
        data=UtilizadorResponse(**novo.__dict__),
        message="Utilizador criado com sucesso.",
    )
