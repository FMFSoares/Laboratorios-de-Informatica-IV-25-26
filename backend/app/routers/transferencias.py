from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.transferencia import (
    PedidoTransferenciaCreate,
    PedidoTransferenciaResponder,
    PedidoTransferenciaResponse,
)
from app.schemas.common import PaginatedResponse, DataResponse
from app.services.transferencia_service import TransferenciaService

router = APIRouter(prefix="/transferencias", tags=["transferencias"])

GESTAO = (PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA)


def get_service(db: Session = Depends(get_db)) -> TransferenciaService:
    return TransferenciaService(db)


@router.post("/", response_model=DataResponse[PedidoTransferenciaResponse], status_code=201)
def criar(
    body: PedidoTransferenciaCreate,
    current_user: CurrentUserResponse = Depends(require_roles(*GESTAO)),
    service: TransferenciaService = Depends(get_service),
):
    return service.criar(body, current_user)


@router.get("/", response_model=PaginatedResponse[PedidoTransferenciaResponse])
def listar(
    estado: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    current_user: CurrentUserResponse = Depends(require_roles(*GESTAO)),
    service: TransferenciaService = Depends(get_service),
):
    return service.listar(estado, page, page_size, current_user)


@router.get("/{pt_id}", response_model=DataResponse[PedidoTransferenciaResponse])
def obter(
    pt_id: int,
    current_user: CurrentUserResponse = Depends(require_roles(*GESTAO)),
    service: TransferenciaService = Depends(get_service),
):
    return service.obter(pt_id, current_user)


@router.post("/{pt_id}/responder", response_model=DataResponse[PedidoTransferenciaResponse])
def responder(
    pt_id: int,
    body: PedidoTransferenciaResponder,
    current_user: CurrentUserResponse = Depends(require_roles(*GESTAO)),
    service: TransferenciaService = Depends(get_service),
):
    return service.responder(pt_id, body, current_user)


@router.post("/{pt_id}/confirmar-recepcao", response_model=DataResponse[PedidoTransferenciaResponse])
def confirmar_recepcao(
    pt_id: int,
    current_user: CurrentUserResponse = Depends(require_roles(*GESTAO)),
    service: TransferenciaService = Depends(get_service),
):
    return service.confirmar_recepcao(pt_id, current_user)


@router.post("/{pt_id}/cancelar", response_model=DataResponse[PedidoTransferenciaResponse])
def cancelar(
    pt_id: int,
    current_user: CurrentUserResponse = Depends(require_roles(*GESTAO)),
    service: TransferenciaService = Depends(get_service),
):
    return service.cancelar(pt_id, current_user)


@router.get("/{pt_id}/pdf")
def obter_pdf(
    pt_id: int,
    current_user: CurrentUserResponse = Depends(require_roles(*GESTAO)),
    service: TransferenciaService = Depends(get_service),
) -> StreamingResponse:
    return service.obter_pdf(pt_id, current_user)
