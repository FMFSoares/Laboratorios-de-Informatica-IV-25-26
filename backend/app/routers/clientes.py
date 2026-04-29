from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import any_authenticated, admin_gerente_or_rececionista
from app.schemas.auth import AuthUserInfo
from app.schemas.cliente import ClienteCreate, ClienteDetalheResponse, ClienteHistoricoItem, ClienteResponse
from app.schemas.common import DataResponse, ErrorResponse, PaginatedResponse
from app.services import cliente_service

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get(
    "",
    response_model=PaginatedResponse[ClienteResponse],
    status_code=200,
    summary="Listar clientes",
    description="Lista clientes com filtro opcional por NIF ou telemóvel. Não-administradores veem apenas clientes da sua loja.",
)
def list_clientes(
    query: str | None = Query(None, description="Pesquisa por NIF ou telemóvel (exact match)."),
    page: int = Query(1, ge=1, description="Página (base 1)."),
    page_size: int = Query(20, ge=1, le=100, description="Resultados por página."),
    current_user: AuthUserInfo = Depends(any_authenticated),
) -> PaginatedResponse[ClienteResponse]:
    return cliente_service.list_clientes(query, page, page_size, current_user)


@router.post(
    "",
    response_model=DataResponse[ClienteResponse],
    status_code=201,
    responses={
        409: {"model": ErrorResponse, "description": "NIF já registado."},
        422: {"description": "Dados inválidos (NIF, telemóvel, RGPD)."},
    },
    summary="Registar cliente",
    description="Regista um novo cliente. Exige consentimento RGPD.",
)
def create_cliente(
    data: ClienteCreate,
    current_user: AuthUserInfo = Depends(admin_gerente_or_rececionista),
) -> DataResponse[ClienteResponse]:
    cliente = cliente_service.create_cliente(data, current_user)
    return DataResponse[ClienteResponse](data=cliente, message="Cliente registado com sucesso.")


@router.get(
    "/{cliente_id}",
    response_model=DataResponse[ClienteDetalheResponse],
    status_code=200,
    responses={
        403: {"model": ErrorResponse, "description": "Acesso a cliente de outra loja."},
        404: {"model": ErrorResponse, "description": "Cliente não encontrado."},
    },
    summary="Detalhe do cliente",
    description="Devolve os dados completos de um cliente, incluindo as trotinetes registadas.",
)
def get_cliente(
    cliente_id: int,
    current_user: AuthUserInfo = Depends(any_authenticated),
) -> DataResponse[ClienteDetalheResponse]:
    cliente = cliente_service.get_cliente(cliente_id, current_user)
    return DataResponse[ClienteDetalheResponse](data=cliente)


@router.get(
    "/{cliente_id}/historico",
    response_model=PaginatedResponse[ClienteHistoricoItem],
    status_code=200,
    responses={
        403: {"model": ErrorResponse, "description": "Acesso a cliente de outra loja."},
        404: {"model": ErrorResponse, "description": "Cliente não encontrado."},
    },
    summary="Histórico do cliente",
    description="Devolve o histórico paginado de ordens de serviço de um cliente.",
)
def get_historico(
    cliente_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: AuthUserInfo = Depends(any_authenticated),
) -> PaginatedResponse[ClienteHistoricoItem]:
    return cliente_service.get_historico(cliente_id, page, page_size, current_user)
