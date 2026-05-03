from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_user, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.cliente import (
    ClienteCreate,
    ClienteDetalheResponse,
    ClienteHistoricoItem,
    ClienteResponse,
)
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.utilizador import PerfilUtilizador
from app.services import cliente_service

router = APIRouter(prefix="/clientes", tags=["clientes"])

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
    response_model=PaginatedResponse[ClienteResponse],
    summary="Listar clientes",
)
def listar(
    query: str | None = Query(None, description="Pesquisa por NIF ou telemóvel (exact match)."),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(_todos),
) -> PaginatedResponse[ClienteResponse]:
    return cliente_service.listar(query, page, page_size, current_user)


@router.post(
    "",
    response_model=DataResponse[ClienteResponse],
    status_code=201,
    summary="Registar cliente",
    responses={
        409: {"description": "NIF duplicado"},
    },
)
def criar(
    body: ClienteCreate,
    current_user: CurrentUserResponse = Depends(_escrita),
) -> DataResponse[ClienteResponse]:
    return cliente_service.criar(body, current_user)


@router.get(
    "/{cliente_id}",
    response_model=DataResponse[ClienteDetalheResponse],
    summary="Detalhe de cliente",
    responses={
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Cliente não encontrado"},
    },
)
def obter(
    cliente_id: int,
    current_user: CurrentUserResponse = Depends(_todos),
) -> DataResponse[ClienteDetalheResponse]:
    return cliente_service.obter(cliente_id, current_user)


@router.get(
    "/{cliente_id}/historico",
    response_model=PaginatedResponse[ClienteHistoricoItem],
    summary="Histórico de ordens do cliente",
    responses={
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Cliente não encontrado"},
    },
)
def historico(
    cliente_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(_todos),
) -> PaginatedResponse[ClienteHistoricoItem]:
    return cliente_service.historico(cliente_id, page, page_size, current_user)
