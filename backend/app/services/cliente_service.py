from __future__ import annotations

from fastapi import HTTPException, status

from app.database import SessionLocal
from app.models.cliente import Cliente
from app.repositories.cliente_repository import ClienteRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.cliente import (
    ClienteCreate,
    ClienteUpdate,
    ClienteDetalheResponse,
    ClienteHistoricoItem,
    ClienteResponse,
)
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.utilizador import PerfilUtilizador
from app.utils.permissions import check_loja_access


def _calcular_fidelizacao(cliente_id: int) -> tuple[int, float]:
    """Returns (nivel, desconto_pct). nivel = floor(log2(n_concluidas+1)), capped at 5."""
    from math import floor, log2
    from app.repositories.ordem_servico_repository import MockOrdemServicoRepository
    oss = MockOrdemServicoRepository().list_by_cliente(cliente_id)
    n = sum(1 for o in oss if o.estado.value in ("CONCLUIDA", "FATURADA"))
    nivel = min(5, int(floor(log2(n + 1))))
    return nivel, float(nivel * 2)


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

        def _enrich(c) -> ClienteResponse:
            nivel, desconto = _calcular_fidelizacao(c.id)
            return ClienteResponse.model_validate(c).model_copy(update={"nivel_fidelizacao": nivel, "desconto_sugerido_pct": desconto})

        return PaginatedResponse[ClienteResponse](
            data=[_enrich(c) for c in clientes_db],
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

        nivel, desconto = _calcular_fidelizacao(cliente_id)
        resp = ClienteDetalheResponse.model_validate(cliente).model_copy(
            update={"nivel_fidelizacao": nivel, "desconto_sugerido_pct": desconto}
        )
        return DataResponse[ClienteDetalheResponse](data=resp)

    def atualizar(self, cliente_id: int, body: ClienteUpdate, current_user: CurrentUserResponse) -> DataResponse[ClienteResponse]:
        cliente = self.repo.get_by_id(cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Cliente não encontrado.", "code": "RESOURCE_NOT_FOUND"},
            )
        check_loja_access(cliente.loja_id, current_user)

        data = body.model_dump(exclude_unset=True)
        updated = self.repo.update(cliente_id, data)
        nivel, desconto = _calcular_fidelizacao(cliente_id)
        resp = ClienteResponse.model_validate(updated).model_copy(
            update={"nivel_fidelizacao": nivel, "desconto_sugerido_pct": desconto}
        )
        return DataResponse[ClienteResponse](data=resp, message="Cliente atualizado com sucesso.")

    def historico(self, cliente_id: int, page: int, page_size: int, current_user: CurrentUserResponse) -> PaginatedResponse[ClienteHistoricoItem]:
        from app.repositories.ordem_servico_repository import MockOrdemServicoRepository
        from app.repositories.trotinete_repository import MockTrotineteRepository
        from app.repositories.fatura_repository import MockFaturaRepository

        cliente = self.repo.get_by_id(cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Cliente não encontrado.", "code": "RESOURCE_NOT_FOUND"},
            )
        check_loja_access(cliente.loja_id, current_user)

        os_repo = MockOrdemServicoRepository()
        trot_repo = MockTrotineteRepository()
        fat_repo = MockFaturaRepository()

        oss = os_repo.list_by_cliente(cliente_id)
        oss.sort(key=lambda o: o.data_entrada, reverse=True)

        items: list[ClienteHistoricoItem] = []
        for os in oss:
            trot = trot_repo.get_by_id(os.trotinete_id)
            valor_final = None
            if os.fatura_id is not None:
                fat = fat_repo.get_by_id(os.fatura_id)
                if fat:
                    valor_final = fat.valor_final
            items.append(ClienteHistoricoItem(
                id=os.id,
                trotinete_numero_serie=trot.numero_serie if trot else "—",
                descricao=os.descricao_problema,
                estado=os.estado.value,
                data_entrada=os.data_entrada,
                data_conclusao=os.data_conclusao,
                valor_final=valor_final,
            ))

        total = len(items)
        start = (page - 1) * page_size
        pages = max(1, -(-total // page_size))
        return PaginatedResponse[ClienteHistoricoItem](
            data=items[start : start + page_size],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )
