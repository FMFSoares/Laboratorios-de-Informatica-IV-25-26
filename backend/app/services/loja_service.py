from fastapi import HTTPException

from app.repositories.loja_repository import LojaRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.common import PaginatedResponse
from app.schemas.loja import LojaResumo, LojaResponse

def check_loja_access(current_user: CurrentUserResponse, loja_id: int):
    if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and current_user.loja_id != loja_id:
        raise HTTPException(status_code=403, detail="Acesso negado a esta loja.")

class LojaService:
    def __init__(self, repo: LojaRepository):
        self.repo = repo

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
    ) -> PaginatedResponse[LojaResumo]:
        if current_user.perfil == PerfilUtilizador.MECANICO:
            loja_id_filtro = current_user.loja_id

        skip = (page - 1) * page_size
        itens, total = self.repo.list(loja_id_filtro, skip, page_size)
        pages = max(1, -(-total // page_size))
        
        return PaginatedResponse[LojaResumo](
            data=itens, total=total, page=page, page_size=page_size, pages=pages
        )

    def obter(self, loja_id: int, current_user: CurrentUserResponse) -> LojaResponse:
        check_loja_access(current_user, loja_id)
        loja = self.repo.get_by_id(loja_id)
        if not loja:
            raise HTTPException(status_code=404, detail="Loja não encontrada.")
        return loja