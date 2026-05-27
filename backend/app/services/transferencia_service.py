from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.repositories.auditoria_repository import AuditoriaRepository
from app.repositories.transferencia_repository import TransferenciaRepository
from app.repositories.stock_repository import StockRepository
from app.repositories.utilizador_repository import UtilizadorRepository
from app.schemas.transferencia import (
    EstadoPedidoTransferencia,
    PedidoTransferenciaCreate,
    PedidoTransferenciaResponder,
    PedidoTransferenciaResponse,
)
from app.schemas.auth import CurrentUserResponse
from app.schemas.auditoria import TipoEventoAuditoria
from app.schemas.notificacao import TipoNotificacao
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.common import PaginatedResponse, DataResponse
from app.services.notificacao_service import criar_notificacao


class TransferenciaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TransferenciaRepository(db)
        self.stock_repo = StockRepository(db)
        self.util_repo = UtilizadorRepository(db)
        self.auditoria_repo = AuditoriaRepository(db)

    def _gerentes_de_loja(self, loja_id: int) -> list:
        return self.util_repo.list_by_perfil(PerfilUtilizador.GERENTE_LOJA, loja_id)

    def _notificar_gerentes(self, loja_id: int, tipo, titulo, mensagem, ref_id):
        for g in self._gerentes_de_loja(loja_id):
            criar_notificacao(self.db, g.id, tipo, titulo, mensagem,
                              referencia_id=ref_id, referencia_tipo="pedido_transferencia")

    def criar(self, body: PedidoTransferenciaCreate, current_user: CurrentUserResponse):
        if current_user.loja_id is None:
            raise HTTPException(status_code=400, detail="Utilizador sem loja associada não pode criar transferências.")
        if body.loja_origem_id == current_user.loja_id:
            raise HTTPException(status_code=400, detail="Não pode pedir peças à sua própria loja.")

        stock = self.stock_repo.get(body.peca_id, body.loja_origem_id)
        disponivel = (stock.quantidade - stock.limite_minimo) if stock else 0
        if body.quantidade > disponivel:
            raise HTTPException(
                status_code=400,
                detail=f"Quantidade indisponível. Máximo pedível: {max(0, disponivel)} unidades (sem baixar o stock mínimo).",
            )

        gerentes_origem = self._gerentes_de_loja(body.loja_origem_id)
        if not gerentes_origem:
            raise HTTPException(status_code=422, detail="Nenhum gerente encontrado na loja de origem")
        gerente_origem_id = gerentes_origem[0].id

        pt = self.repo.create(
            loja_origem_id=body.loja_origem_id,
            loja_destino_id=current_user.loja_id,
            gerente_origem_id=gerente_origem_id,
            gerente_destino_id=current_user.id,
            peca_id=body.peca_id,
            quantidade=body.quantidade,
            estado=EstadoPedidoTransferencia.PENDENTE,
            data_pedido=datetime.now(timezone.utc),
            observacoes_pedido=body.observacoes,
        )

        self._notificar_gerentes(
            body.loja_origem_id,
            TipoNotificacao.PEDIDO_TRANSFERENCIA,
            "Novo pedido de transferência",
            f"{current_user.nome} pediu {body.quantidade}x {pt.peca.nome if pt.peca else ''} da sua loja.",
            pt.id,
        )
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.TRANSFERENCIA_CRIADA,
            descricao=f"Pedido de transferência de {body.quantidade}x '{pt.peca.nome if pt.peca else ''}' da loja #{body.loja_origem_id}",
            utilizador_id=current_user.id,
            loja_id=current_user.loja_id,
            detalhe={"pedido_id": pt.id, "peca_id": body.peca_id, "quantidade": body.quantidade, "loja_origem_id": body.loja_origem_id, "loja_destino_id": current_user.loja_id},
        )
        self.db.commit()
        pt = self.repo.get_by_id(pt.id)
        return DataResponse[PedidoTransferenciaResponse](
            data=PedidoTransferenciaResponse.model_validate(pt),
            message="Pedido criado com sucesso.",
        )

    def listar(
        self, estado: str | None, page: int, page_size: int, current_user: CurrentUserResponse
    ) -> PaginatedResponse[PedidoTransferenciaResponse]:
        loja_id = None if current_user.perfil == PerfilUtilizador.ADMINISTRADOR else current_user.loja_id
        estado_enum = EstadoPedidoTransferencia(estado) if estado else None
        skip = (page - 1) * page_size
        itens, total = self.repo.list(loja_id, estado_enum, skip, page_size)
        pages = max(1, -(-total // page_size))
        return PaginatedResponse[PedidoTransferenciaResponse](
            data=[PedidoTransferenciaResponse.model_validate(i) for i in itens],
            total=total, page=page, page_size=page_size, pages=pages,
        )

    def obter(self, pt_id: int, current_user: CurrentUserResponse):
        pt = self.repo.get_by_id(pt_id)
        if not pt:
            raise HTTPException(status_code=404, detail="Pedido não encontrado.")
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
            if current_user.loja_id not in (pt.loja_origem_id, pt.loja_destino_id):
                raise HTTPException(status_code=403, detail="Acesso negado.")
        return DataResponse[PedidoTransferenciaResponse](data=PedidoTransferenciaResponse.model_validate(pt))

    def responder(self, pt_id: int, body: PedidoTransferenciaResponder, current_user: CurrentUserResponse):
        pt = self.repo.get_by_id(pt_id)
        if not pt:
            raise HTTPException(status_code=404, detail="Pedido não encontrado.")
        if pt.estado != EstadoPedidoTransferencia.PENDENTE:
            raise HTTPException(status_code=409, detail="Pedido já foi respondido.")
        if current_user.loja_id != pt.loja_origem_id and current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
            raise HTTPException(status_code=403, detail="Só o gerente da loja de origem pode responder.")

        agora = datetime.now(timezone.utc)
        pt.data_resposta = agora
        pt.observacoes_resposta = body.observacoes

        peca_nome = pt.peca.nome if pt.peca else f"peça #{pt.peca_id}"
        if body.aceitar:
            self.stock_repo.consumir(pt.peca_id, pt.loja_origem_id, pt.quantidade)
            pt.estado = EstadoPedidoTransferencia.ACEITE
            pt.data_assinatura_origem = agora
            self._notificar_gerentes(
                pt.loja_destino_id,
                TipoNotificacao.TRANSFERENCIA_ACEITE,
                "Transferência aceite",
                f"O seu pedido de {pt.quantidade}x {peca_nome} foi aceite. Confirme a receção quando chegar.",
                pt.id,
            )
        else:
            pt.estado = EstadoPedidoTransferencia.RECUSADO
            self._notificar_gerentes(
                pt.loja_destino_id,
                TipoNotificacao.TRANSFERENCIA_RECUSADA,
                "Transferência recusada",
                f"O seu pedido de {pt.quantidade}x {peca_nome} foi recusado.",
                pt.id,
            )

        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.TRANSFERENCIA_RESPONDIDA,
            descricao=f"Pedido de transferência #{pt_id} {'aceite' if body.aceitar else 'recusado'} — {pt.quantidade}x '{peca_nome}'",
            utilizador_id=current_user.id,
            loja_id=pt.loja_origem_id,
            detalhe={"pedido_id": pt_id, "aceite": body.aceitar, "peca_id": pt.peca_id, "quantidade": pt.quantidade},
        )
        self.db.commit()
        self.db.refresh(pt)
        return DataResponse[PedidoTransferenciaResponse](
            data=PedidoTransferenciaResponse.model_validate(pt),
            message="Resposta registada.",
        )

    def confirmar_recepcao(self, pt_id: int, current_user: CurrentUserResponse):
        pt = self.repo.get_by_id(pt_id)
        if not pt:
            raise HTTPException(status_code=404, detail="Pedido não encontrado.")
        if pt.estado != EstadoPedidoTransferencia.ACEITE:
            raise HTTPException(status_code=409, detail="Pedido não está em estado ACEITE.")
        if current_user.loja_id != pt.loja_destino_id and current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
            raise HTTPException(status_code=403, detail="Só o gerente da loja de destino pode confirmar.")

        agora = datetime.now(timezone.utc)
        peca_nome = pt.peca.nome if pt.peca else f"peça #{pt.peca_id}"
        self.stock_repo.adicionar(pt.peca_id, pt.loja_destino_id, pt.quantidade)
        pt.estado = EstadoPedidoTransferencia.CONCLUIDA
        pt.data_recepcao = agora
        pt.data_assinatura_destino = agora

        self._notificar_gerentes(
            pt.loja_origem_id,
            TipoNotificacao.TRANSFERENCIA_CONCLUIDA,
            "Transferência concluída",
            f"A loja de destino confirmou a receção de {pt.quantidade}x {peca_nome}.",
            pt.id,
        )
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.TRANSFERENCIA_RECEPCAO_CONFIRMADA,
            descricao=f"Receção confirmada — {pt.quantidade}x '{peca_nome}' na loja #{pt.loja_destino_id}",
            utilizador_id=current_user.id,
            loja_id=pt.loja_destino_id,
            detalhe={"pedido_id": pt_id, "peca_id": pt.peca_id, "quantidade": pt.quantidade, "loja_origem_id": pt.loja_origem_id, "loja_destino_id": pt.loja_destino_id},
        )
        self.db.commit()
        self.db.refresh(pt)
        return DataResponse[PedidoTransferenciaResponse](
            data=PedidoTransferenciaResponse.model_validate(pt),
            message="Receção confirmada.",
        )

    def cancelar(self, pt_id: int, current_user: CurrentUserResponse):
        pt = self.repo.get_by_id(pt_id)
        if not pt:
            raise HTTPException(status_code=404, detail="Pedido não encontrado.")
        if pt.estado != EstadoPedidoTransferencia.PENDENTE:
            raise HTTPException(status_code=409, detail="Só pedidos PENDENTE podem ser cancelados.")
        if current_user.loja_id != pt.loja_destino_id and current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
            raise HTTPException(status_code=403, detail="Só o gerente solicitante pode cancelar.")

        pt.estado = EstadoPedidoTransferencia.CANCELADO
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.TRANSFERENCIA_CANCELADA,
            descricao=f"Pedido de transferência #{pt_id} cancelado",
            utilizador_id=current_user.id,
            loja_id=pt.loja_destino_id,
            detalhe={"pedido_id": pt_id, "peca_id": pt.peca_id, "quantidade": pt.quantidade},
        )
        self.db.commit()
        self.db.refresh(pt)
        return DataResponse[PedidoTransferenciaResponse](
            data=PedidoTransferenciaResponse.model_validate(pt),
            message="Pedido cancelado.",
        )

    def obter_pdf(self, pt_id: int, current_user: CurrentUserResponse) -> StreamingResponse:
        pt = self.repo.get_by_id(pt_id)
        if not pt:
            raise HTTPException(status_code=404, detail="Pedido não encontrado.")
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
            if current_user.loja_id not in (pt.loja_origem_id, pt.loja_destino_id):
                raise HTTPException(status_code=403, detail="Acesso negado.")

        from app.utils.pdf import gerar_pdf_transferencia
        pdf_bytes = gerar_pdf_transferencia(pt)
        import io
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{pt.numero}.pdf"'},
        )
