from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import CurrentUserResponse
from app.auth.dependencies import get_current_user, require_roles
from app.schemas.utilizador import PerfilUtilizador
from app.services.ordem_servico_service import OrdemServicoService

router = APIRouter(prefix="/ordens-servico", tags=["ordens de serviço"])

def get_os_service(db: Session = Depends(get_db)) -> OrdemServicoService:
    return OrdemServicoService(db)

@router.get("/")
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
    service: OrdemServicoService = Depends(get_os_service)
):
    return service.listar(
        loja_id, estado, mecanico_id, data_inicio, data_fim, 
        em_atraso, page, page_size, current_user
    )

@router.get("/{os_id}")
def obter_ordem_servico(
    os_id: int,
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: OrdemServicoService = Depends(get_os_service)
):
    # Irás envolver este retorno com DataResponse[OrdemServicoDetalheResponse]
    return {"data": service.obter(os_id, current_user)}

@router.patch("/{os_id}/estado")
def atualizar_estado_os(
    os_id: int,
    novo_estado: str, # Definido pelo teu payload
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: OrdemServicoService = Depends(get_os_service)
):
    return service.atualizar_estado(os_id, novo_estado, current_user)

@router.post("/{os_id}/pecas", status_code=status.HTTP_201_CREATED)
def adicionar_peca(
    os_id: int, peca_id: int, quantidade: int, # Estes args vêm do teu body Request Schema
    current_user: CurrentUserResponse = Depends(require_roles(PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA, PerfilUtilizador.MECANICO)),
    service: OrdemServicoService = Depends(get_os_service)
):
    return service.adicionar_peca(os_id, peca_id, quantidade, current_user)