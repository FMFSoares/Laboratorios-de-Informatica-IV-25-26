from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.peca import CategoriaPeca, PecaCreate, PecaDetalheResponse, PecaResponse
from app.schemas.utilizador import PerfilUtilizador
from app.services import peca_service

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


@router.get(
    "",
    response_model=PaginatedResponse[PecaResponse],
    summary="Listar catálogo de peças",
)
def listar(
    query: str | None = Query(None, description="Pesquisa por nome ou referência."),
    categoria: CategoriaPeca | None = Query(None, description="Filtrar por categoria."),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: CurrentUserResponse = Depends(_todos),
) -> PaginatedResponse[PecaResponse]:
    return peca_service.listar(query, categoria, page, page_size)


@router.get(
    "/{peca_id}",
    response_model=DataResponse[PecaDetalheResponse],
    summary="Detalhe de peça",
    responses={404: {"description": "Peça não encontrada"}},
)
def obter(
    peca_id: int,
    _: CurrentUserResponse = Depends(_todos),
) -> DataResponse[PecaDetalheResponse]:
    return peca_service.obter(peca_id)


@router.post(
    "",
    response_model=DataResponse[PecaResponse],
    status_code=201,
    summary="Criar peça no catálogo",
    responses={409: {"description": "Referência duplicada"}},
)
def criar(
    body: PecaCreate,
    _: CurrentUserResponse = Depends(_escrita),
) -> DataResponse[PecaResponse]:
    return peca_service.criar(body)
