from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.auth.dependencies import require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.fatura import FaturaCreateRequest, FaturaEnviarEmailRequest, FaturaResponse, FaturaResumo
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


@router.post(
    "/{fatura_id}/enviar-email",
    summary="Enviar fatura por email com PDF em anexo",
    responses={
        400: {"description": "NO_EMAIL — nem o cliente nem o pedido têm email"},
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Fatura não encontrada"},
    },
)
def enviar_email(
    fatura_id: int,
    body: FaturaEnviarEmailRequest,
    current_user: CurrentUserResponse = Depends(_autorizados),
) -> dict:
    return fatura_service.enviar_email(fatura_id, body, current_user)


@router.get(
    "/{fatura_id}/pdf",
    summary="Descarregar PDF da fatura",
    response_class=Response,
    responses={
        200: {"content": {"application/pdf": {}}, "description": "PDF da fatura"},
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Fatura não encontrada"},
    },
)
def descarregar_pdf(
    fatura_id: int,
    current_user: CurrentUserResponse = Depends(_autorizados),
) -> Response:
    pdf_bytes = fatura_service.descarregar_pdf(fatura_id, current_user)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="fatura-{fatura_id}.pdf"'},
    )


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
