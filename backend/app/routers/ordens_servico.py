from __future__ import annotations

from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, Query

from app.auth.dependencies import get_current_user, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.ordem_servico import (
    EstadoOrdemServico,
    OrdemServicoCreate,
    OrdemServicoDetalheResponse,
    OrdemServicoEstadoUpdate,
    OrdemServicoEstadoUpdateResponse,
    OrdemServicoMecanicoUpdate,
    OrdemServicoMecanicoUpdateResponse,
    OrdemServicoResponse,
    OrdemServicoResumo,
    PecaAplicadaRequest,
    PecaAplicadaResponse,
    TempoInicioResponse,
    TempoParagemResponse,
)
from app.schemas.utilizador import PerfilUtilizador
from app.services import ordem_servico_service

router = APIRouter(prefix="/ordens-servico", tags=["ordens de serviço"])

_todos = require_roles(
    PerfilUtilizador.ADMINISTRADOR,
    PerfilUtilizador.GERENTE_LOJA,
    PerfilUtilizador.RECECIONISTA,
    PerfilUtilizador.MECANICO,
)
_criacao = require_roles(
    PerfilUtilizador.ADMINISTRADOR,
    PerfilUtilizador.GERENTE_LOJA,
    PerfilUtilizador.RECECIONISTA,
)
_tecnicos = require_roles(
    PerfilUtilizador.ADMINISTRADOR,
    PerfilUtilizador.GERENTE_LOJA,
    PerfilUtilizador.MECANICO,
)


@router.post(
    "",
    response_model=DataResponse[OrdemServicoResponse],
    status_code=201,
    summary="Criar ordem de serviço",
    responses={
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Trotinete ou mecânico não encontrado"},
    },
)
def criar(
    body: OrdemServicoCreate,
    current_user: CurrentUserResponse = Depends(_criacao),
) -> DataResponse[OrdemServicoResponse]:
    return ordem_servico_service.criar(body, current_user)


@router.get(
    "",
    response_model=PaginatedResponse[OrdemServicoResumo],
    summary="Listar ordens de serviço",
)
def listar(
    loja_id: int | None = Query(None, description="Filtrar por loja (ADMINISTRADOR apenas)."),
    estado: EstadoOrdemServico | None = Query(None, description="Filtrar por estado."),
    mecanico_id: int | None = Query(None, description="Filtrar por mecânico."),
    data_inicio: date | None = Query(None, description="Data de entrada a partir de (ISO 8601)."),
    data_fim: date | None = Query(None, description="Data de entrada até (ISO 8601)."),
    em_atraso: bool | None = Query(None, description="Se true, devolve apenas OS cujo tempo decorrido supera a média das concluídas (RF17)."),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(_todos),
) -> PaginatedResponse[OrdemServicoResumo]:
    return ordem_servico_service.listar(
        loja_id, estado, mecanico_id, data_inicio, data_fim, em_atraso, page, page_size, current_user
    )


@router.get(
    "/{os_id}",
    response_model=DataResponse[OrdemServicoDetalheResponse],
    summary="Detalhe de ordem de serviço",
    responses={
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Ordem não encontrada"},
    },
)
def obter(
    os_id: int,
    current_user: CurrentUserResponse = Depends(_todos),
) -> DataResponse[OrdemServicoDetalheResponse]:
    return ordem_servico_service.obter(os_id, current_user)


@router.patch(
    "/{os_id}/estado",
    response_model=DataResponse[OrdemServicoEstadoUpdateResponse],
    summary="Atualizar estado da ordem de serviço",
    responses={
        403: {"description": "PERMISSION_DENIED ou LOJA_MISMATCH"},
        404: {"description": "Ordem não encontrada"},
        409: {"description": "INVALID_STATE_TRANSITION"},
    },
)
def atualizar_estado(
    os_id: int,
    body: OrdemServicoEstadoUpdate,
    background_tasks: BackgroundTasks,
    current_user: CurrentUserResponse = Depends(get_current_user),
) -> DataResponse[OrdemServicoEstadoUpdateResponse]:
    # RBAC por transição é verificado no service
    return ordem_servico_service.atualizar_estado(os_id, body, current_user, background_tasks)


@router.patch(
    "/{os_id}/mecanico",
    response_model=DataResponse[OrdemServicoMecanicoUpdateResponse],
    summary="Reatribuir ou desatribuir mecânico",
    responses={
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Ordem ou mecânico não encontrado"},
        409: {"description": "INVALID_STATE_TRANSITION — OS já concluída ou cancelada"},
    },
)
def atualizar_mecanico(
    os_id: int,
    body: OrdemServicoMecanicoUpdate,
    current_user: CurrentUserResponse = Depends(_criacao),
) -> DataResponse[OrdemServicoMecanicoUpdateResponse]:
    return ordem_servico_service.atualizar_mecanico(os_id, body, current_user)


@router.post(
    "/{os_id}/tempos/iniciar",
    response_model=DataResponse[TempoInicioResponse],
    summary="Iniciar registo de tempo (métricas internas)",
    responses={409: {"description": "INVALID_STATE_TRANSITION | MECANICO_TIMER_CONFLICT — inclui os_conflito_id e os_conflito_numero no body para o frontend apresentar diálogo de confirmação"}},
)
def iniciar_tempo(
    os_id: int,
    current_user: CurrentUserResponse = Depends(_tecnicos),
) -> DataResponse[TempoInicioResponse]:
    return ordem_servico_service.iniciar_tempo(os_id, current_user)


@router.post(
    "/{os_id}/tempos/parar",
    response_model=DataResponse[TempoParagemResponse],
    summary="Parar registo de tempo (métricas internas)",
    responses={409: {"description": "Nenhum tempo em curso"}},
)
def parar_tempo(
    os_id: int,
    current_user: CurrentUserResponse = Depends(_tecnicos),
) -> DataResponse[TempoParagemResponse]:
    return ordem_servico_service.parar_tempo(os_id, current_user)


@router.post(
    "/{os_id}/pecas",
    response_model=DataResponse[PecaAplicadaResponse],
    status_code=201,
    summary="Adicionar peça à ordem de serviço",
    responses={
        400: {"description": "INSUFFICIENT_STOCK"},
        404: {"description": "Peça não encontrada"},
        409: {"description": "OS em estado que não permite adicionar peças"},
    },
)
def adicionar_peca(
    os_id: int,
    body: PecaAplicadaRequest,
    current_user: CurrentUserResponse = Depends(_tecnicos),
) -> DataResponse[PecaAplicadaResponse]:
    return ordem_servico_service.adicionar_peca(os_id, body, current_user)
