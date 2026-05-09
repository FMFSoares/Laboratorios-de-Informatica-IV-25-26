from __future__ import annotations

from fastapi import HTTPException, status

from app.database import SessionLocal
from app.models.cliente import Cliente
from app.repositories.cliente_repository import ClienteRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.cliente import (
    ClienteCreate,
    ClienteDetalheResponse,
    ClienteHistoricoItem,
    ClienteResponse,
)
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.utilizador import PerfilUtilizador
from app.utils.permissions import check_loja_access


def _find(cliente_id: int) -> Cliente | None:
    """Cross-service lookup. Uses its own DB session — keeps other services decoupled from FastAPI DI."""
    db = SessionLocal()
    try:
        return ClienteRepository(db).get_by_id(cliente_id)
    finally:
        db.close()


class ClienteService:
    def __init__(self, repo: ClienteRepository):
        self.repo = repo

    def listar(self, query: str | None, page: int, page_size: int, current_user: CurrentUserResponse) -> PaginatedResponse[ClienteResponse]:
        loja_id = current_user.loja_id if current_user.perfil != PerfilUtilizador.ADMINISTRADOR else None
        skip = (page - 1) * page_size

        total = self.repo.count(loja_id=loja_id, query_str=query)
        clientes_db = self.repo.get_all(skip=skip, limit=page_size, loja_id=loja_id, query_str=query)
        pages = max(1, -(-total // page_size))

        return PaginatedResponse[ClienteResponse](
            data=[ClienteResponse.model_validate(c) for c in clientes_db],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    def criar(self, body: ClienteCreate, current_user: CurrentUserResponse) -> DataResponse[ClienteResponse]:
        if self.repo.get_by_nif(body.nif):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"detail": "NIF já registado.", "code": "DUPLICATE_ENTRY"}
            )

        loja_id = current_user.loja_id or 1
        novo_cliente = self.repo.create(body, loja_id)

        return DataResponse[ClienteResponse](
            data=ClienteResponse.model_validate(novo_cliente),
            message="Cliente registado com sucesso.",
        )

    def obter(self, cliente_id: int, current_user: CurrentUserResponse) -> DataResponse[ClienteDetalheResponse]:
        cliente = self.repo.get_by_id(cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Cliente não encontrado.", "code": "RESOURCE_NOT_FOUND"},
            )
        check_loja_access(cliente.loja_id, current_user)

        # O SQLAlchemy relation mapeia automaticamente a "lista de trotinetes" atráves do Pydantic
        return DataResponse[ClienteDetalheResponse](
            data=ClienteDetalheResponse.model_validate(cliente),
        )

    def historico(self, cliente_id: int, page: int, page_size: int, current_user: CurrentUserResponse) -> PaginatedResponse[ClienteHistoricoItem]:
        cliente = self.repo.get_by_id(cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Cliente não encontrado.", "code": "RESOURCE_NOT_FOUND"},
            )
        check_loja_access(cliente.loja_id, current_user)

        # Futuramente substituir por queries às ordens de serviço do cliente
        return PaginatedResponse[ClienteHistoricoItem](
            data=[],
            total=0,
            page=page,
            page_size=page_size,
            pages=1,
        )
