from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.utilizador import PerfilUtilizador, UtilizadorCreate, UtilizadorResponse
from app.services.utilizador_service import UtilizadorService

router = APIRouter(prefix="/utilizadores", tags=["gestão de utilizadores"])

# Proteção forte usando RBAC (Apenas Administradores têm acesso ao CRUD de staff)
_admin_only = require_roles(PerfilUtilizador.ADMINISTRADOR)

def get_utilizador_service(db: Session = Depends(get_db)) -> UtilizadorService:
    return UtilizadorService(db)


@router.get(
    "",
    response_model=PaginatedResponse[UtilizadorResponse],
    summary="Listar staff (Apenas Administrador)",
)
def listar(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: CurrentUserResponse = Depends(_admin_only),
    service: UtilizadorService = Depends(get_utilizador_service),
) -> PaginatedResponse[UtilizadorResponse]:
    return service.listar_utilizadores(page, page_size)


@router.post(
    "",
    response_model=DataResponse[UtilizadorResponse],
    status_code=201,
    summary="Criar novo membro de staff (Apenas Administrador)",
)
def criar(
    body: UtilizadorCreate,
    _: CurrentUserResponse = Depends(_admin_only),
    service: UtilizadorService = Depends(get_utilizador_service),
) -> DataResponse[UtilizadorResponse]:
    return service.criar_utilizador(body)