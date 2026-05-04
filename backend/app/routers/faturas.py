from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.fatura import FaturaCreateRequest, FaturaResponse, FaturaResumo
from app.schemas.utilizador import PerfilUtilizador
from app.services import fatura_service

router = APIRouter(prefix="/faturas", tags=["faturas"])

_autorizados = require_roles(
    PerfilUtilizador.ADMINISTRADOR,
    PerfilUtilizador.GERENTE_LOJA,
    PerfilUtilizador.RECECIONISTA,
)


@router.post(
    "",
    response_model=DataResponse[FaturaResponse],
    status_code=201,
    summary="Emitir fatura para OS concluída",
    responses={
        400: {"description": "ORDER_NOT_CONCLUDED"},
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Ordem de serviço não encontrada"},
        409: {"description": "ORDER_ALREADY_INVOICED"},
    },
)
def emitir(
    body: FaturaCreateRequest,
    current_user: CurrentUserResponse = Depends(_autorizados),
) -> DataResponse[FaturaResponse]:
    return fatura_service.emitir(body.ordem_servico_id, current_user)


@router.get(
    "/{fatura_id}",
    response_model=DataResponse[FaturaResponse],
    summary="Detalhe de fatura",
    responses={
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Fatura não encontrada"},
    },
)
def obter(
    fatura_id: int,
    current_user: CurrentUserResponse = Depends(_autorizados),
) -> DataResponse[FaturaResponse]:
    return fatura_service.obter(fatura_id, current_user)


@router.get(
    "",
    response_model=PaginatedResponse[FaturaResumo],
    summary="Listar faturas",
)
def listar(
    ordem_servico_id: int | None = Query(None, description="Filtrar pela OS associada."),
    loja_id: int | None = Query(None, description="Filtrar por loja (ADMINISTRADOR apenas)."),
    data_inicio: date | None = Query(None, description="Data de emissão a partir de (ISO 8601)."),
    data_fim: date | None = Query(None, description="Data de emissão até (ISO 8601)."),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(_autorizados),
) -> PaginatedResponse[FaturaResumo]:
    return fatura_service.listar(
        ordem_servico_id, loja_id, data_inicio, data_fim, page, page_size, current_user
    )
