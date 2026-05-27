from fastapi import HTTPException

from app.repositories.auditoria_repository import AuditoriaRepository
from app.repositories.loja_repository import LojaRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.auditoria import TipoEventoAuditoria
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.common import PaginatedResponse, DataResponse
from app.schemas.loja import LojaCreate, LojaUpdate, LojaResumo, LojaResponse
from app.utils.permissions import check_loja_access

class LojaService:
    def __init__(self, repo: LojaRepository):
        self.repo = repo
        self.auditoria_repo = AuditoriaRepository(self.repo.db)

    def get_nome(self, loja_id: int) -> str | None:
        return self.repo.get_nome(loja_id)

    def get_telefone(self, loja_id: int) -> str | None:
        return self.repo.get_telefone(loja_id)

    def listar(
        self,
        loja_id_filtro: int | None,
        page: int,
        page_size: int,
        current_user: CurrentUserResponse
    ) -> PaginatedResponse[LojaResponse]:
        if current_user.perfil == PerfilUtilizador.MECANICO:
            loja_id_filtro = current_user.loja_id

        skip = (page - 1) * page_size
        itens, total = self.repo.list(loja_id_filtro, skip, page_size)
        pages = max(1, -(-total // page_size))

        return PaginatedResponse[LojaResponse](
            data=[LojaResponse.model_validate(l) for l in itens],
            total=total, page=page, page_size=page_size, pages=pages
        )

    def obter(self, loja_id: int, current_user: CurrentUserResponse) -> LojaResponse:
        check_loja_access(loja_id, current_user)
        loja = self.repo.get_by_id(loja_id)
        if not loja:
            raise HTTPException(status_code=404, detail="Loja não encontrada.")
        return loja

    def criar(self, body: LojaCreate, current_user: CurrentUserResponse) -> DataResponse[LojaResponse]:
        nova = self.repo.create(
            nome=body.nome,
            cidade=body.cidade,
            morada=body.morada,
            telefone=body.telefone,
            email=body.email,
        )
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.LOJA_CRIADA,
            descricao=f"Loja '{body.nome}' ({body.cidade}) criada",
            utilizador_id=current_user.id,
            detalhe={"nome": body.nome, "cidade": body.cidade},
        )
        self.repo.db.commit()
        return DataResponse[LojaResponse](data=LojaResponse.model_validate(nova), message="Loja criada com sucesso.")

    def atualizar(self, loja_id: int, body: LojaUpdate, current_user: CurrentUserResponse) -> DataResponse[LojaResponse]:
        loja = self.repo.get_by_id(loja_id)
        if not loja:
            raise HTTPException(status_code=404, detail="Loja não encontrada.")
        updates = body.model_dump(exclude_unset=True)
        loja = self.repo.update(loja, **updates)
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.LOJA_ATUALIZADA,
            descricao=f"Loja '{loja.nome}' atualizada",
            utilizador_id=current_user.id,
            loja_id=loja_id,
            detalhe={"loja_id": loja_id, "campos": list(updates.keys())},
        )
        self.repo.db.commit()
        return DataResponse[LojaResponse](data=LojaResponse.model_validate(loja), message="Loja atualizada.")