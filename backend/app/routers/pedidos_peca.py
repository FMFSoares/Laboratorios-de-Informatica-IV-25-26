from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.transferencia import PedidoPecaCreate, PedidoPecaResponder, PedidoPecaResponse
from app.schemas.common import PaginatedResponse, DataResponse
from app.services.pedido_peca_service import PedidoPecaService

router = APIRouter(prefix="/pedidos-peca", tags=["pedidos-peca"])


def get_service(db: Session = Depends(get_db)) -> PedidoPecaService:
    return PedidoPecaService(db)


@router.post("/", response_model=DataResponse[PedidoPecaResponse], status_code=201)
def criar(
    body: PedidoPecaCreate,
    current_user: CurrentUserResponse = Depends(require_roles(PerfilUtilizador.MECANICO)),
    service: PedidoPecaService = Depends(get_service),
):
    return service.criar(body, current_user)


@router.get("/", response_model=PaginatedResponse[PedidoPecaResponse])
def listar(
    estado: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: PedidoPecaService = Depends(get_service),
):
    return service.listar(estado, page, page_size, current_user)


@router.post("/{pp_id}/responder", response_model=DataResponse[PedidoPecaResponse])
def responder(
    pp_id: int,
    body: PedidoPecaResponder,
    current_user: CurrentUserResponse = Depends(
        require_roles(PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA)
    ),
    service: PedidoPecaService = Depends(get_service),
):
    return service.responder(pp_id, body, current_user)
