from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories.peca_repository import MockPecaRepository, Peca
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.peca import CategoriaPeca, PecaCreate, PecaDetalheResponse, PecaResponse

_repo = MockPecaRepository()


def _to_response(p: Peca) -> PecaResponse:
    return PecaResponse(**p.__dict__)


def _to_detalhe(p: Peca) -> PecaDetalheResponse:
    return PecaDetalheResponse(**p.__dict__)


def get_peca_interna(peca_id: int) -> Peca | None:
    """Full peca object (includes preco_custo) for internal use by other services."""
    return _repo.get_by_id(peca_id)


def listar(
    query: str | None,
    categoria: CategoriaPeca | None,
    page: int,
    page_size: int,
) -> PaginatedResponse[PecaResponse]:
    itens, total = _repo.list(query, categoria, page, page_size)
    pages = max(1, -(-total // page_size))

    return PaginatedResponse[PecaResponse](
        data=[_to_response(p) for p in itens],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def obter(peca_id: int) -> DataResponse[PecaDetalheResponse]:
    peca = _repo.get_by_id(peca_id)
    if peca is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Peça não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )
    return DataResponse[PecaDetalheResponse](data=_to_detalhe(peca))


def criar(body: PecaCreate) -> DataResponse[PecaResponse]:
    if _repo.exists_referencia(body.referencia):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Referência já registada no sistema.", "code": "DUPLICATE_ENTRY"},
        )

    nova = _repo.create(
        referencia=body.referencia,
        nome=body.nome,
        categoria=body.categoria,
        descricao=body.descricao,
        unidade=body.unidade,
        preco_custo=body.preco_custo,
        preco_venda=body.preco_venda,
    )

    return DataResponse[PecaResponse](
        data=_to_response(nova),
        message="Peça criada com sucesso.",
    )
