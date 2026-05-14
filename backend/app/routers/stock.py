from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.stock import (
    StockEntradaRequest,
    StockEntradaResponse,
    StockItemResponse,
    StockMinimoUpdate,
    StockTransferenciaRequest,
    StockTransferenciaResponse,
)
from app.schemas.utilizador import PerfilUtilizador
from app.services import stock_service

router = APIRouter(prefix="/stock", tags=["stock"])

_todos = require_roles(
    PerfilUtilizador.ADMINISTRADOR,
    PerfilUtilizador.GERENTE_LOJA,
    PerfilUtilizador.RECECIONISTA,
    PerfilUtilizador.MECANICO,
)
_gestao = require_roles(
    PerfilUtilizador.ADMINISTRADOR,
    PerfilUtilizador.GERENTE_LOJA,
)


@router.get(
    "",
    response_model=PaginatedResponse[StockItemResponse],
    summary="Consultar stock",
)
def listar(
    loja_id: int | None = Query(None, description="Filtrar por loja (só ADMINISTRADOR)."),
    alerta: bool = Query(False, description="Se true, devolve apenas peças abaixo do limite mínimo."),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(_todos),
) -> PaginatedResponse[StockItemResponse]:
    return stock_service.listar(loja_id, alerta, page, page_size, current_user)


@router.patch(
    "/{peca_id}/minimo",
    response_model=DataResponse[StockItemResponse],
    summary="Atualizar limite mínimo de stock de uma peça numa loja",
    responses={
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Peça ou loja não encontrada"},
    },
)
def atualizar_minimo(
    peca_id: int,
    body: StockMinimoUpdate,
    current_user: CurrentUserResponse = Depends(_gestao),
) -> DataResponse[StockItemResponse]:
    return stock_service.atualizar_minimo(peca_id, body.loja_id, body.limite_minimo, current_user)


@router.post(
    "/entradas",
    response_model=DataResponse[StockEntradaResponse],
    status_code=201,
    summary="Registar entrada de stock",
    responses={
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Peça ou loja não encontrada"},
    },
)
def entrada(
    body: StockEntradaRequest,
    current_user: CurrentUserResponse = Depends(_gestao),
) -> DataResponse[StockEntradaResponse]:
    return stock_service.entrada(body, current_user)


@router.post(
    "/transferencias",
    response_model=DataResponse[StockTransferenciaResponse],
    status_code=201,
    summary="Transferir stock entre lojas",
    responses={
        400: {"description": "INSUFFICIENT_STOCK"},
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Peça ou loja não encontrada"},
    },
)
def transferencia(
    body: StockTransferenciaRequest,
    current_user: CurrentUserResponse = Depends(_gestao),
) -> DataResponse[StockTransferenciaResponse]:
    return stock_service.transferencia(body, current_user)
