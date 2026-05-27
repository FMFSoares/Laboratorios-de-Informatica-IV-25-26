from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.cliente import (
    ClienteCreate,
    ClienteUpdate,
    ClienteDetalheResponse,
    ClienteHistoricoItem,
    ClienteResponse,
)
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.utilizador import PerfilUtilizador
from app.database import get_db
from app.repositories.cliente_repository import ClienteRepository
from app.services.cliente_service import ClienteService

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

# Helper de injeção de dependências do FastAPI
def get_cliente_service(db: Session = Depends(get_db)) -> ClienteService:
    repo = ClienteRepository(db)
    return ClienteService(repo)


@router.get(
    "",
    response_model=PaginatedResponse[ClienteResponse],
    summary="Listar clientes",
)
def listar(
    query: str | None = Query(None, description="Pesquisa por nome, NIF, telemóvel ou email (partial match)."),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(_todos),
    service: ClienteService = Depends(get_cliente_service),
) -> PaginatedResponse[ClienteResponse]:
    return service.listar(query, page, page_size, current_user)


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
    service: ClienteService = Depends(get_cliente_service),
) -> DataResponse[ClienteResponse]:
    return service.criar(body, current_user)


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
    service: ClienteService = Depends(get_cliente_service),
) -> DataResponse[ClienteDetalheResponse]:
    return service.obter(cliente_id, current_user)


@router.patch(
    "/{cliente_id}",
    response_model=DataResponse[ClienteResponse],
    summary="Atualizar dados do cliente",
    responses={
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Cliente não encontrado"},
    },
)
def atualizar(
    cliente_id: int,
    body: ClienteUpdate,
    current_user: CurrentUserResponse = Depends(_escrita),
    service: ClienteService = Depends(get_cliente_service),
) -> DataResponse[ClienteResponse]:
    return service.atualizar(cliente_id, body, current_user)


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
    service: ClienteService = Depends(get_cliente_service),
) -> PaginatedResponse[ClienteHistoricoItem]:
    return service.historico(cliente_id, page, page_size, current_user)
