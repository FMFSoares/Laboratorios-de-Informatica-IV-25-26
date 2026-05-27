from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.peca import CategoriaPeca, PecaCreate, PecaUpdate, PecaDetalheResponse, PecaResponse
from app.schemas.utilizador import PerfilUtilizador
from app.services.peca_service import PecaService
from app.repositories.peca_repository import PecaRepository

router = APIRouter(prefix="/pecas", tags=["peças"])

_todos = require_roles(
    PerfilUtilizador.ADMINISTRADOR,
    PerfilUtilizador.GERENTE_LOJA,
    PerfilUtilizador.RECECIONISTA,
    PerfilUtilizador.MECANICO,
)
_escrita = require_roles(
    PerfilUtilizador.ADMINISTRADOR,
    PerfilUtilizador.GERENTE_LOJA,
)

def get_peca_service(db: Session = Depends(get_db)) -> PecaService:
    return PecaService(PecaRepository(db))

@router.get(
    "",
    response_model=PaginatedResponse[PecaDetalheResponse],
    summary="Listar catálogo de peças",
)
def listar(
    query: str | None = Query(None, description="Pesquisa por nome ou referência."),
    categoria: CategoriaPeca | None = Query(None, description="Filtrar por categoria."),
    incluir_inativos: bool = Query(False, description="Incluir peças inativas (uso interno)."),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: CurrentUserResponse = Depends(_todos),
    service: PecaService = Depends(get_peca_service),
) -> PaginatedResponse[PecaDetalheResponse]:
    return service.listar(query, categoria, page, page_size, incluir_inativos=incluir_inativos)


@router.get(
    "/{peca_id}",
    response_model=DataResponse[PecaDetalheResponse],
    summary="Detalhe de peça",
    responses={404: {"description": "Peça não encontrada"}},
)
def obter(
    peca_id: int,
    _: CurrentUserResponse = Depends(_todos),
    service: PecaService = Depends(get_peca_service),
) -> DataResponse[PecaDetalheResponse]:
    return service.obter(peca_id)


@router.post(
    "",
    response_model=DataResponse[PecaResponse],
    status_code=201,
    summary="Criar peça no catálogo",
    responses={409: {"description": "Referência duplicada"}},
)
def criar(
    body: PecaCreate,
    current_user: CurrentUserResponse = Depends(_escrita),
    service: PecaService = Depends(get_peca_service),
) -> DataResponse[PecaResponse]:
    return service.criar(body, current_user)


@router.patch(
    "/{peca_id}",
    response_model=DataResponse[PecaDetalheResponse],
    summary="Actualizar peça no catálogo",
    responses={404: {"description": "Peça não encontrada"}},
)
def atualizar(
    peca_id: int,
    body: PecaUpdate,
    current_user: CurrentUserResponse = Depends(_escrita),
    service: PecaService = Depends(get_peca_service),
) -> DataResponse[PecaDetalheResponse]:
    return service.atualizar(peca_id, body, current_user)
