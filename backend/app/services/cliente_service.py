from __future__ import annotations

from math import floor, log2

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.ordem_servico import OrdemServico, EstadoOrdemServico
from app.repositories.auditoria_repository import AuditoriaRepository
from app.repositories.cliente_repository import ClienteRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.auditoria import TipoEventoAuditoria
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


def _calcular_fidelizacao_from_db(db: Session, cliente_id: int) -> tuple[int, float]:
    """Returns (nivel, desconto_pct) using the caller's session to avoid opening a new connection."""
    n = db.query(OrdemServico).filter(
        OrdemServico.cliente_id == cliente_id,
        OrdemServico.estado.in_([EstadoOrdemServico.CONCLUIDA, EstadoOrdemServico.FATURADA]),
    ).count()
    nivel = min(5, int(floor(log2(n + 1))))
    return nivel, float(nivel * 2)


class ClienteService:
    def __init__(self, repo: ClienteRepository):
        self.repo = repo
        self.auditoria_repo = AuditoriaRepository(self.repo.db)

    def listar(self, query: str | None, page: int, page_size: int, current_user: CurrentUserResponse) -> PaginatedResponse[ClienteResponse]:
        loja_id = current_user.loja_id if current_user.perfil != PerfilUtilizador.ADMINISTRADOR else None
        skip = (page - 1) * page_size

        total = self.repo.count(loja_id=loja_id, query_str=query)
        clientes_db = self.repo.get_all(skip=skip, limit=page_size, loja_id=loja_id, query_str=query)
        pages = max(1, -(-total // page_size))

        def _enrich(c) -> ClienteResponse:
            nivel, desconto = _calcular_fidelizacao_from_db(self.repo.db, c.id)
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
                status_code=status.HTTP_409_CONFLICT,
                detail={"detail": "NIF já registado.", "code": "DUPLICATE_ENTRY"}
            )

        loja_id = current_user.loja_id
        if loja_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"detail": "Administrador deve especificar uma loja.", "code": "MISSING_LOJA"}
            )
        novo_cliente = self.repo.create(body, loja_id)

        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.CLIENTE_CRIADO,
            descricao=f"Cliente '{body.nome}' (NIF: {body.nif}) registado",
            utilizador_id=current_user.id,
            loja_id=loja_id,
            detalhe={"nome": body.nome, "nif": body.nif},
        )
        self.repo.db.commit()

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

        nivel, desconto = _calcular_fidelizacao_from_db(self.repo.db, cliente_id)
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
        nivel, desconto = _calcular_fidelizacao_from_db(self.repo.db, cliente_id)

        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.CLIENTE_ATUALIZADO,
            descricao=f"Dados do cliente '{cliente.nome}' atualizados",
            utilizador_id=current_user.id,
            loja_id=cliente.loja_id,
            detalhe={"cliente_id": cliente_id, "campos": list(data.keys())},
        )
        self.repo.db.commit()

        resp = ClienteResponse.model_validate(updated).model_copy(
            update={"nivel_fidelizacao": nivel, "desconto_sugerido_pct": desconto}
        )
        return DataResponse[ClienteResponse](data=resp, message="Cliente atualizado com sucesso.")

    def historico(self, cliente_id: int, page: int, page_size: int, current_user: CurrentUserResponse) -> PaginatedResponse[ClienteHistoricoItem]:
        from app.repositories.ordem_servico_repository import OrdemServicoRepository

        cliente = self.repo.get_by_id(cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Cliente não encontrado.", "code": "RESOURCE_NOT_FOUND"},
            )
        check_loja_access(cliente.loja_id, current_user)

        oss = OrdemServicoRepository(self.repo.db).list_by_cliente(cliente_id)

        items: list[ClienteHistoricoItem] = []
        for os in oss:
            valor_final = os.fatura.valor_final if os.fatura else None
            items.append(ClienteHistoricoItem(
                id=os.id,
                trotinete_numero_serie=os.trotinete.numero_serie if os.trotinete else "—",
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
