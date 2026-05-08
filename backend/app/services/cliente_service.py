from __future__ import annotations

from fastapi import HTTPException, status

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


class ClienteService:
    def __init__(self, repo: ClienteRepository):
        self.repo = repo

    def _check_loja(self, loja_id: int, current_user: CurrentUserResponse) -> None:
        if current_user.perfil == PerfilUtilizador.ADMINISTRADOR:
            return
        if loja_id != current_user.loja_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "detail": "Acesso a dados de outra loja não permitido.",
                    "code": "LOJA_MISMATCH",
                },
            )

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
        self._check_loja(cliente.loja_id, current_user)

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
        self._check_loja(cliente.loja_id, current_user)

        # Futuramente substituir por queries às ordens de serviço do cliente
        return PaginatedResponse[ClienteHistoricoItem](
            data=[],
            total=0,
            page=page,
            page_size=page_size,
            pages=1,
        )
