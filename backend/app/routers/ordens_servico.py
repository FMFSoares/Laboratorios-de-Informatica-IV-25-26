from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import CurrentUserResponse
from app.auth.dependencies import get_current_user, require_roles
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.common import PaginatedResponse, DataResponse
from app.schemas.auditoria import AuditoriaItemResponse
from app.schemas.ordem_servico import (
    OrdemServicoCreate,
    OrdemServicoResumo,
    OrdemServicoDetalheResponse,
    OrdemServicoEstadoUpdate,
    PecaAplicadaRequest,
    PecaAplicadaResponse,
    OrdemServicoMecanicoUpdate,
    TempoInicioResponse,
    TempoParagemResponse,
    OrdemServicoObservacaoCreate,
    OrdemServicoObservacaoResponse,
    DiagnosticoSubmit,
)
from app.services.ordem_servico_service import OrdemServicoService

router = APIRouter(prefix="/ordens-servico", tags=["ordens de serviço"])


def get_os_service(db: Session = Depends(get_db)) -> OrdemServicoService:
    return OrdemServicoService(db)


@router.get("/", response_model=PaginatedResponse[OrdemServicoResumo])
def listar_ordens_servico(
    loja_id: int | None = Query(None),
    estado: str | None = Query(None),
    mecanico_id: int | None = Query(None),
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    em_atraso: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: OrdemServicoService = Depends(get_os_service),
):
    return service.listar(
        loja_id, estado, mecanico_id, data_inicio, data_fim,
        em_atraso, page, page_size, current_user,
    )


@router.post("/", response_model=DataResponse[OrdemServicoDetalheResponse], status_code=status.HTTP_201_CREATED)
def criar_ordem_servico(
    body: OrdemServicoCreate,
    current_user: CurrentUserResponse = Depends(
        require_roles(
            PerfilUtilizador.ADMINISTRADOR,
            PerfilUtilizador.GERENTE_LOJA,
            PerfilUtilizador.RECECIONISTA,
        )
    ),
    service: OrdemServicoService = Depends(get_os_service),
):
    return DataResponse[OrdemServicoDetalheResponse](data=service.criar(body, current_user))


@router.get("/{os_id}", response_model=DataResponse[OrdemServicoDetalheResponse])
def obter_ordem_servico(
    os_id: int,
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: OrdemServicoService = Depends(get_os_service),
):
    return DataResponse[OrdemServicoDetalheResponse](data=service.obter(os_id, current_user))


@router.patch("/{os_id}/estado", response_model=DataResponse[OrdemServicoDetalheResponse])
def atualizar_estado_os(
    os_id: int,
    body: OrdemServicoEstadoUpdate,
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: OrdemServicoService = Depends(get_os_service),
):
    os = service.atualizar_estado(os_id, body.novo_estado.value, current_user)
    return DataResponse[OrdemServicoDetalheResponse](data=os)


@router.delete("/{os_id}/pecas/{peca_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_peca(
    os_id: int,
    peca_id: int,
    current_user: CurrentUserResponse = Depends(
        require_roles(
            PerfilUtilizador.ADMINISTRADOR,
            PerfilUtilizador.GERENTE_LOJA,
            PerfilUtilizador.MECANICO,
        )
    ),
    service: OrdemServicoService = Depends(get_os_service),
):
    service.remover_peca(os_id, peca_id, current_user)


@router.post("/{os_id}/pecas", response_model=DataResponse[PecaAplicadaResponse], status_code=status.HTTP_201_CREATED)
def adicionar_peca(
    os_id: int,
    body: PecaAplicadaRequest,
    current_user: CurrentUserResponse = Depends(
        require_roles(
            PerfilUtilizador.ADMINISTRADOR,
            PerfilUtilizador.GERENTE_LOJA,
            PerfilUtilizador.MECANICO,
        )
    ),
    service: OrdemServicoService = Depends(get_os_service),
):
    peca_os = service.adicionar_peca(os_id, body.peca_id, body.quantidade, current_user)
    return DataResponse[PecaAplicadaResponse](data=peca_os)


@router.post("/{os_id}/tempos/iniciar", response_model=DataResponse[TempoInicioResponse], status_code=status.HTTP_201_CREATED)
def iniciar_tempo(
    os_id: int,
    current_user: CurrentUserResponse = Depends(require_roles(PerfilUtilizador.MECANICO, PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA)),
    service: OrdemServicoService = Depends(get_os_service),
):
    return DataResponse[TempoInicioResponse](data=service.iniciar_tempo(os_id, current_user))


@router.post("/{os_id}/tempos/parar", response_model=DataResponse[TempoParagemResponse])
def parar_tempo(
    os_id: int,
    current_user: CurrentUserResponse = Depends(require_roles(PerfilUtilizador.MECANICO, PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA)),
    service: OrdemServicoService = Depends(get_os_service),
):
    return DataResponse[TempoParagemResponse](data=service.parar_tempo(os_id, current_user))


@router.patch("/{os_id}/mecanico", response_model=DataResponse[OrdemServicoDetalheResponse])
def atualizar_mecanico_os(
    os_id: int,
    body: OrdemServicoMecanicoUpdate,
    current_user: CurrentUserResponse = Depends(
        require_roles(PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA, PerfilUtilizador.RECECIONISTA)
    ),
    service: OrdemServicoService = Depends(get_os_service),
):
    return DataResponse[OrdemServicoDetalheResponse](data=service.atualizar_mecanico(os_id, body.mecanico_id, current_user))


@router.post("/{os_id}/diagnostico", response_model=DataResponse[OrdemServicoDetalheResponse])
def submeter_diagnostico(
    os_id: int,
    body: DiagnosticoSubmit,
    current_user: CurrentUserResponse = Depends(
        require_roles(PerfilUtilizador.MECANICO, PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA)
    ),
    service: OrdemServicoService = Depends(get_os_service),
):
    return DataResponse[OrdemServicoDetalheResponse](data=service.submeter_diagnostico(os_id, body, current_user))


@router.get("/{os_id}/historico", response_model=DataResponse[list[AuditoriaItemResponse]])
def historico_os(
    os_id: int,
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: OrdemServicoService = Depends(get_os_service),
):
    return DataResponse(data=service.historico_os(os_id, current_user))


@router.delete("/{os_id}", status_code=204)
def apagar_os(
    os_id: int,
    current_user: CurrentUserResponse = Depends(require_roles(PerfilUtilizador.ADMINISTRADOR)),
    service: OrdemServicoService = Depends(get_os_service),
):
    service.apagar(os_id, current_user)


@router.post("/{os_id}/observacoes", response_model=DataResponse[OrdemServicoObservacaoResponse], status_code=status.HTTP_201_CREATED)
def adicionar_observacao(
    os_id: int,
    body: OrdemServicoObservacaoCreate,
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: OrdemServicoService = Depends(get_os_service),
):
    return DataResponse[OrdemServicoObservacaoResponse](data=service.adicionar_observacao(os_id, body, current_user))
