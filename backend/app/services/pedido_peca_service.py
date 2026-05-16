from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.pedido_peca_repository import PedidoPecaRepository
from app.repositories.ordem_servico_repository import OrdemServicoRepository
from app.repositories.utilizador_repository import UtilizadorRepository
from app.schemas.transferencia import (
    EstadoPedidoPeca,
    PedidoPecaCreate,
    PedidoPecaResponder,
    PedidoPecaResponse,
)
from app.schemas.auth import CurrentUserResponse
from app.schemas.notificacao import TipoNotificacao
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.common import PaginatedResponse, DataResponse
from app.services.notificacao_service import criar_notificacao


class PedidoPecaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PedidoPecaRepository(db)
        self.os_repo = OrdemServicoRepository(db)
        self.util_repo = UtilizadorRepository(db)

    def _gerentes_de_loja(self, loja_id: int) -> list:
        return self.util_repo.list_by_perfil(PerfilUtilizador.GERENTE_LOJA, loja_id)

    def criar(self, body: PedidoPecaCreate, current_user: CurrentUserResponse):
        os = self.os_repo.get_by_id(body.ordem_servico_id)
        if not os:
            raise HTTPException(status_code=404, detail="OS não encontrada.")
        if os.loja_id != current_user.loja_id:
            raise HTTPException(status_code=403, detail="OS não pertence à sua loja.")

        pp = self.repo.create(
            ordem_servico_id=body.ordem_servico_id,
            mecanico_id=current_user.id,
            loja_id=current_user.loja_id,
            peca_id=body.peca_id,
            quantidade=body.quantidade,
            estado=EstadoPedidoPeca.PENDENTE,
            data_pedido=datetime.now(timezone.utc),
            observacoes=body.observacoes,
        )
        self.db.flush()

        peca_nome = pp.peca.nome if pp.peca else f"peça #{body.peca_id}"
        for g in self._gerentes_de_loja(current_user.loja_id):
            criar_notificacao(
                self.db, g.id,
                TipoNotificacao.PEDIDO_PECA,
                "Pedido de peça em falta",
                f"{current_user.nome} precisa de {body.quantidade}x {peca_nome} para a OS #{os.numero}.",
                referencia_id=pp.id,
                referencia_tipo="pedido_peca",
            )

        self.db.commit()
        self.db.refresh(pp)
        return DataResponse[PedidoPecaResponse](
            data=PedidoPecaResponse.model_validate(pp),
            message="Pedido enviado.",
        )

    def responder(self, pp_id: int, body: PedidoPecaResponder, current_user: CurrentUserResponse):
        pp = self.repo.get_by_id(pp_id)
        if not pp:
            raise HTTPException(status_code=404, detail="Pedido não encontrado.")
        if pp.estado != EstadoPedidoPeca.PENDENTE:
            raise HTTPException(status_code=409, detail="Pedido já foi respondido.")
        if current_user.loja_id != pp.loja_id and current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
            raise HTTPException(status_code=403, detail="Acesso negado.")

        pp.estado = EstadoPedidoPeca.APROVADO if body.aprovar else EstadoPedidoPeca.RECUSADO
        pp.data_resposta = datetime.now(timezone.utc)
        pp.observacoes = body.observacoes or pp.observacoes

        tipo = TipoNotificacao.PECA_APROVADA if body.aprovar else TipoNotificacao.PECA_RECUSADA
        titulo = "Pedido de peça aprovado" if body.aprovar else "Pedido de peça recusado"
        peca_nome = pp.peca.nome if pp.peca else "peça"
        criar_notificacao(
            self.db, pp.mecanico_id, tipo, titulo,
            f"O pedido de {pp.quantidade}x {peca_nome} foi {'aprovado' if body.aprovar else 'recusado'}.",
            referencia_id=pp.id, referencia_tipo="pedido_peca",
        )

        self.db.commit()
        self.db.refresh(pp)
        return DataResponse[PedidoPecaResponse](
            data=PedidoPecaResponse.model_validate(pp),
            message="Resposta registada.",
        )

    def listar(self, estado: str | None, page: int, page_size: int, current_user: CurrentUserResponse):
        estado_enum = EstadoPedidoPeca(estado) if estado else None
        skip = (page - 1) * page_size

        if current_user.perfil == PerfilUtilizador.MECANICO:
            itens, total = self.repo.list_by_mecanico(current_user.id, skip, page_size)
        else:
            loja_id = current_user.loja_id if current_user.perfil != PerfilUtilizador.ADMINISTRADOR else None
            if loja_id:
                itens, total = self.repo.list_by_loja(loja_id, estado_enum, skip, page_size)
            else:
                itens, total = self.repo.list_by_loja(0, estado_enum, skip, page_size)

        pages = max(1, -(-total // page_size))
        return PaginatedResponse[PedidoPecaResponse](
            data=[PedidoPecaResponse.model_validate(i) for i in itens],
            total=total, page=page, page_size=page_size, pages=pages,
        )
