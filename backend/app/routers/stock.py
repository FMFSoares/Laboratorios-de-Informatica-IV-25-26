from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles, get_current_user
from app.schemas.auth import CurrentUserResponse
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.common import PaginatedResponse, DataResponse
from app.schemas.stock import StockItemResponse, StockEntradaRequest, StockEntradaResponse, StockTransferenciaRequest, StockTransferenciaResponse
from app.services.stock_service import StockService

router = APIRouter(prefix="/stock", tags=["stock"])

def get_stock_service(db: Session = Depends(get_db)) -> StockService:
    return StockService(db)

@router.get("/", response_model=PaginatedResponse[StockItemResponse])
def listar_stock(
    loja_id: int | None = Query(None),
    apenas_alertas: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: StockService = Depends(get_stock_service)
):
    return service.listar(loja_id, apenas_alertas, page, page_size, current_user)

@router.post("/entradas", response_model=DataResponse[StockEntradaResponse], status_code=status.HTTP_201_CREATED)
def registar_entrada(
    body: StockEntradaRequest,
    current_user: CurrentUserResponse = Depends(require_roles(PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA)),
    service: StockService = Depends(get_stock_service)
):
    return service.entrada(body, current_user)

@router.post("/transferencias", response_model=DataResponse[StockTransferenciaResponse], status_code=status.HTTP_201_CREATED)
def registar_transferencia(
    body: StockTransferenciaRequest,
    current_user: CurrentUserResponse = Depends(require_roles(PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA)),
    service: StockService = Depends(get_stock_service)
):
    return service.transferencia(body, current_user)