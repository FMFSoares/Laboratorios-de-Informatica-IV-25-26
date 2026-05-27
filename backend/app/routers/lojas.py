from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.loja import LojaCreate, LojaUpdate, LojaResponse, LojaResumo
from app.schemas.common import PaginatedResponse, DataResponse
from app.schemas.auth import CurrentUserResponse
from app.auth.dependencies import get_current_user, require_roles
from app.services.loja_service import LojaService
from app.repositories.loja_repository import LojaRepository
from app.schemas.utilizador import PerfilUtilizador

router = APIRouter(prefix="/lojas", tags=["lojas"])

_admin_only = require_roles(PerfilUtilizador.ADMINISTRADOR)

def get_loja_service(db: Session = Depends(get_db)) -> LojaService:
    return LojaService(LojaRepository(db))

@router.get("/", response_model=PaginatedResponse[LojaResponse])
def listar_lojas(
    loja_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: LojaService = Depends(get_loja_service)
):
    return service.listar(
        loja_id_filtro=loja_id, page=page, page_size=page_size, current_user=current_user
    )

@router.get("/{loja_id}", response_model=DataResponse[LojaResponse])
def obter_loja(
    loja_id: int,
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: LojaService = Depends(get_loja_service)
):
    loja = service.obter(loja_id=loja_id, current_user=current_user)
    return DataResponse[LojaResponse](data=loja)


@router.post("/", response_model=DataResponse[LojaResponse], status_code=201, summary="Criar loja (Apenas Administrador)")
def criar_loja(
    body: LojaCreate,
    current_user: CurrentUserResponse = Depends(_admin_only),
    service: LojaService = Depends(get_loja_service),
):
    return service.criar(body, current_user)


@router.patch("/{loja_id}", response_model=DataResponse[LojaResponse], summary="Actualizar loja (Apenas Administrador)")
def atualizar_loja(
    loja_id: int,
    body: LojaUpdate,
    current_user: CurrentUserResponse = Depends(_admin_only),
    service: LojaService = Depends(get_loja_service),
):
    return service.atualizar(loja_id, body, current_user)