from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles, get_current_user
from app.schemas.auth import CurrentUserResponse
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.trotinete import TrotineteCreate, TrotineteResponse, TrotineteDetalheResponse
from app.services.trotinete_service import TrotineteService

router = APIRouter(prefix="/trotinetes", tags=["trotinetes"])

_todos = get_current_user
_escrita = require_roles(
    PerfilUtilizador.ADMINISTRADOR,
    PerfilUtilizador.GERENTE_LOJA,
    PerfilUtilizador.RECECIONISTA,
)

def get_trotinete_service(db: Session = Depends(get_db)) -> TrotineteService:
    return TrotineteService(db)

@router.get("", response_model=PaginatedResponse[TrotineteResponse])
def listar(
    cliente_id: int | None = Query(None),
    query: str | None = Query(None, description="Pesquisa por série, marca, modelo ou nome do cliente (partial match)."),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(_todos),
    service: TrotineteService = Depends(get_trotinete_service)
):
    return service.listar(cliente_id, query, page, page_size, current_user)

@router.get("/{trotinete_id}", response_model=DataResponse[TrotineteDetalheResponse])
def obter(
    trotinete_id: int,
    current_user: CurrentUserResponse = Depends(_todos),
    service: TrotineteService = Depends(get_trotinete_service)
):
    return service.obter(trotinete_id, current_user)

@router.post("", response_model=DataResponse[TrotineteResponse], status_code=201)
def criar(
    body: TrotineteCreate,
    current_user: CurrentUserResponse = Depends(_escrita),
    service: TrotineteService = Depends(get_trotinete_service)
):
    return service.criar(body, current_user)


@router.delete("/{trotinete_id}", status_code=204)
def apagar(
    trotinete_id: int,
    current_user: CurrentUserResponse = Depends(require_roles(PerfilUtilizador.ADMINISTRADOR)),
    service: TrotineteService = Depends(get_trotinete_service),
):
    service.apagar(trotinete_id, current_user)