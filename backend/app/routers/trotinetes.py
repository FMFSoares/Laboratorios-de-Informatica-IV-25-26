from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.trotinete import (
    TrotineteCreate,
    TrotineteDetalheResponse,
    TrotineteResponse,
)
from app.schemas.utilizador import PerfilUtilizador
from app.services import trotinete_service

router = APIRouter(prefix="/trotinetes", tags=["trotinetes"])

_todos = require_roles(
    PerfilUtilizador.ADMINISTRADOR,
    PerfilUtilizador.GERENTE_LOJA,
    PerfilUtilizador.RECECIONISTA,
    PerfilUtilizador.MECANICO,
)
_escrita = require_roles(
    PerfilUtilizador.ADMINISTRADOR,
    PerfilUtilizador.GERENTE_LOJA,
    PerfilUtilizador.RECECIONISTA,
)


@router.get(
    "",
    response_model=PaginatedResponse[TrotineteResponse],
    summary="Listar trotinetes",
)
def listar(
    cliente_id: int | None = Query(None, description="Filtrar por cliente."),
    numero_serie: str | None = Query(None, description="Pesquisa por número de série (exact match)."),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(_todos),
) -> PaginatedResponse[TrotineteResponse]:
    return trotinete_service.listar(cliente_id, numero_serie, page, page_size, current_user)


@router.post(
    "",
    response_model=DataResponse[TrotineteResponse],
    status_code=201,
    summary="Registar trotinete",
    responses={
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Cliente não encontrado"},
        409: {"description": "Número de série duplicado"},
    },
)
def criar(
    body: TrotineteCreate,
    current_user: CurrentUserResponse = Depends(_escrita),
) -> DataResponse[TrotineteResponse]:
    return trotinete_service.criar(body, current_user)


@router.get(
    "/{trotinete_id}",
    response_model=DataResponse[TrotineteDetalheResponse],
    summary="Detalhe de trotinete",
    responses={
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Trotinete não encontrada"},
    },
)
def obter(
    trotinete_id: int,
    current_user: CurrentUserResponse = Depends(_todos),
) -> DataResponse[TrotineteDetalheResponse]:
    return trotinete_service.obter(trotinete_id, current_user)
