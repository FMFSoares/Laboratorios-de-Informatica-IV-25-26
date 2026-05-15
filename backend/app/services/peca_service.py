from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories.peca_repository import PecaRepository
from app.models.peca import Peca
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.peca import CategoriaPeca, PecaCreate, PecaDetalheResponse, PecaResponse

class PecaService:
    def __init__(self, repo: PecaRepository):
        self.repo = repo

    def _to_response(self, p: Peca) -> PecaResponse:
        data = {k: v for k, v in p.__dict__.items() if not k.startswith("_")}
        return PecaResponse(**data)

    def _to_detalhe(self, p: Peca) -> PecaDetalheResponse:
        data = {k: v for k, v in p.__dict__.items() if not k.startswith("_")}
        return PecaDetalheResponse(**data)

    def get_peca_interna(self, peca_id: int) -> Peca | None:
        """Full peca object (includes preco_custo) for internal use by other services."""
        return self.repo.get_by_id(peca_id)

    def listar(
        self,
        query: str | None,
        categoria: CategoriaPeca | None,
        page: int,
        page_size: int,
    ) -> PaginatedResponse[PecaResponse]:
        skip = (page - 1) * page_size
        itens, total = self.repo.list(query, categoria, skip, page_size)
        pages = max(1, -(-total // page_size))

        return PaginatedResponse[PecaResponse](
            data=[self._to_response(p) for p in itens],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    def obter(self, peca_id: int) -> DataResponse[PecaDetalheResponse]:
        peca = self.repo.get_by_id(peca_id)
        if peca is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Peça não encontrada.", "code": "RESOURCE_NOT_FOUND"},
            )
        return DataResponse[PecaDetalheResponse](data=self._to_detalhe(peca))

    def criar(self, body: PecaCreate) -> DataResponse[PecaResponse]:
        if self.repo.exists_referencia(body.referencia):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"detail": "Referência já registada no sistema.", "code": "DUPLICATE_ENTRY"},
            )

        nova = self.repo.create(
            referencia=body.referencia,
            nome=body.nome,
            categoria=body.categoria,
            descricao=body.descricao,
            unidade=body.unidade,
            preco_custo=body.preco_custo,
            preco_venda=body.preco_venda,
        )

        return DataResponse[PecaResponse](
            data=self._to_response(nova),
            message="Peça criada com sucesso.",
        )
