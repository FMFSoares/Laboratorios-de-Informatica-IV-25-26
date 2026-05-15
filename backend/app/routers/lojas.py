from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.loja import LojaResponse, LojaResumo
from app.schemas.common import PaginatedResponse, DataResponse
from app.schemas.auth import CurrentUserResponse
from app.auth.dependencies import get_current_user
from app.services.loja_service import LojaService
from app.repositories.loja_repository import LojaRepository

router = APIRouter(prefix="/lojas", tags=["lojas"])

def get_loja_service(db: Session = Depends(get_db)) -> LojaService:
    return LojaService(LojaRepository(db))

@router.get("/", response_model=PaginatedResponse[LojaResumo])
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