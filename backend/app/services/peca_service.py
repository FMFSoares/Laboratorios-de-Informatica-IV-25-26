from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories.auditoria_repository import AuditoriaRepository
from app.repositories.peca_repository import PecaRepository
from app.models.peca import Peca
from app.schemas.auth import CurrentUserResponse
from app.schemas.auditoria import TipoEventoAuditoria
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.peca import CategoriaPeca, PecaCreate, PecaUpdate, PecaDetalheResponse, PecaResponse

class PecaService:
    def __init__(self, repo: PecaRepository):
        self.repo = repo
        self.auditoria_repo = AuditoriaRepository(self.repo.db)

    def _to_response(self, p: Peca) -> PecaResponse:
        return PecaResponse.model_validate(p)

    def _to_detalhe(self, p: Peca) -> PecaDetalheResponse:
        return PecaDetalheResponse.model_validate(p)

    def get_peca_interna(self, peca_id: int) -> Peca | None:
        """Full peca object (includes preco_custo) for internal use by other services."""
        return self.repo.get_by_id(peca_id)

    def listar(
        self,
        query: str | None,
        categoria: CategoriaPeca | None,
        page: int,
        page_size: int,
        incluir_inativos: bool = False,
    ) -> PaginatedResponse[PecaDetalheResponse]:
        skip = (page - 1) * page_size
        itens, total = self.repo.list(query, categoria, skip, page_size, incluir_inativos=incluir_inativos)
        pages = max(1, -(-total // page_size))

        return PaginatedResponse[PecaDetalheResponse](
            data=[self._to_detalhe(p) for p in itens],
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

    def criar(self, body: PecaCreate, current_user: CurrentUserResponse) -> DataResponse[PecaResponse]:
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

        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.PECA_CRIADA,
            descricao=f"Peça '{body.nome}' (ref: {body.referencia}) criada no catálogo",
            utilizador_id=current_user.id,
            detalhe={"referencia": body.referencia, "nome": body.nome, "categoria": body.categoria},
        )
        self.repo.db.commit()

        return DataResponse[PecaResponse](
            data=self._to_response(nova),
            message="Peça criada com sucesso.",
        )

    def atualizar(self, peca_id: int, body: PecaUpdate, current_user: CurrentUserResponse) -> DataResponse[PecaDetalheResponse]:
        peca = self.repo.get_by_id(peca_id)
        if peca is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Peça não encontrada.", "code": "RESOURCE_NOT_FOUND"},
            )
        updates = body.model_dump(exclude_unset=True)
        peca = self.repo.update(peca, **updates)

        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.PECA_ATUALIZADA,
            descricao=f"Peça '{peca.nome}' atualizada",
            utilizador_id=current_user.id,
            detalhe={"peca_id": peca_id, "campos": list(updates.keys())},
        )
        self.repo.db.commit()

        return DataResponse[PecaDetalheResponse](
            data=self._to_detalhe(peca),
            message="Peça atualizada com sucesso.",
        )
