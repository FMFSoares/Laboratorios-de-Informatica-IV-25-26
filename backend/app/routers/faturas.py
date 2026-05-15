from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.fatura import FaturaCreateRequest, FaturaResponse, FaturaResumo
from app.schemas.common import PaginatedResponse, DataResponse
from app.schemas.auth import CurrentUserResponse
from app.schemas.utilizador import PerfilUtilizador
from app.auth.dependencies import require_roles, get_current_user
from app.services.fatura_service import FaturaService

router = APIRouter(prefix="/faturas", tags=["faturas"])

def get_fatura_service(db: Session = Depends(get_db)) -> FaturaService:
    return FaturaService(db)

@router.post("/", response_model=DataResponse[FaturaResponse], status_code=status.HTTP_201_CREATED)
def emitir_fatura(
    body: FaturaCreateRequest,
    current_user: CurrentUserResponse = Depends(require_roles(PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA, PerfilUtilizador.RECECIONISTA)),
    service: FaturaService = Depends(get_fatura_service)
):
    fatura = service.emitir(body, current_user)
    return DataResponse[FaturaResponse](message="Fatura emitida com sucesso.", data=fatura)

@router.get("/{fatura_id}", response_model=DataResponse[FaturaResponse])
def obter_fatura(
    fatura_id: int,
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: FaturaService = Depends(get_fatura_service)
):
    fatura = service.obter(fatura_id, current_user)
    return DataResponse[FaturaResponse](data=fatura)

@router.get("/", response_model=PaginatedResponse[FaturaResumo])
def listar_faturas(
    loja_id: int | None = Query(None),
    ordem_servico_id: int | None = Query(None),
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: FaturaService = Depends(get_fatura_service)
):
    return service.listar(loja_id, ordem_servico_id, data_inicio, data_fim, page, page_size, current_user)

@router.get("/{fatura_id}/pdf")
def descarregar_pdf(
    fatura_id: int, current_user: CurrentUserResponse = Depends(get_current_user), service: FaturaService = Depends(get_fatura_service)
):
    return service.descarregar_pdf(fatura_id, current_user)

@router.post("/{fatura_id}/email")
def enviar_email(
    fatura_id: int, current_user: CurrentUserResponse = Depends(get_current_user), service: FaturaService = Depends(get_fatura_service)
):
    return service.enviar_email(fatura_id, current_user)