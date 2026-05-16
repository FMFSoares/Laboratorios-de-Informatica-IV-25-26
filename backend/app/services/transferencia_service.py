from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

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

    def _gerentes_de_loja(self, loja_id: int) -> list:
        return self.util_repo.list_by_perfil(PerfilUtilizador.GERENTE_LOJA, loja_id)

    def _notificar_gerentes(self, loja_id: int, tipo, titulo, mensagem, ref_id):
        for g in self._gerentes_de_loja(loja_id):
            criar_notificacao(self.db, g.id, tipo, titulo, mensagem,
                              referencia_id=ref_id, referencia_tipo="pedido_transferencia")

    def criar(self, body: PedidoTransferenciaCreate, current_user: CurrentUserResponse):
        if body.loja_origem_id == current_user.loja_id:
            raise HTTPException(status_code=400, detail="Não pode pedir peças à sua própria loja.")

        stock = self.stock_repo.get(body.peca_id, body.loja_origem_id)
        disponivel = (stock.quantidade - stock.limite_minimo) if stock else 0
        if body.quantidade > disponivel:
            raise HTTPException(
                status_code=400,
                detail=f"Quantidade indisponível. Máximo pedível: {max(0, disponivel)} unidades (sem baixar o stock mínimo).",
            )

        pt = self.repo.create(
            loja_origem_id=body.loja_origem_id,
            loja_destino_id=current_user.loja_id,
            gerente_origem_id=self._gerentes_de_loja(body.loja_origem_id)[0].id if self._gerentes_de_loja(body.loja_origem_id) else current_user.id,
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

        if body.aceitar:
            self.stock_repo.consumir(pt.peca_id, pt.loja_origem_id, pt.quantidade)
            pt.estado = EstadoPedidoTransferencia.ACEITE
            pt.data_assinatura_origem = agora
            self._notificar_gerentes(
                pt.loja_destino_id,
                TipoNotificacao.TRANSFERENCIA_ACEITE,
                "Transferência aceite",
                f"O seu pedido de {pt.quantidade}x {pt.peca.nome if pt.peca else ''} foi aceite. Confirme a receção quando chegar.",
                pt.id,
            )
        else:
            pt.estado = EstadoPedidoTransferencia.RECUSADO
            self._notificar_gerentes(
                pt.loja_destino_id,
                TipoNotificacao.TRANSFERENCIA_RECUSADA,
                "Transferência recusada",
                f"O seu pedido de {pt.quantidade}x {pt.peca.nome if pt.peca else ''} foi recusado.",
                pt.id,
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
        self.stock_repo.adicionar(pt.peca_id, pt.loja_destino_id, pt.quantidade)
        pt.estado = EstadoPedidoTransferencia.CONCLUIDA
        pt.data_recepcao = agora
        pt.data_assinatura_destino = agora

        self._notificar_gerentes(
            pt.loja_origem_id,
            TipoNotificacao.TRANSFERENCIA_CONCLUIDA,
            "Transferência concluída",
            f"A loja de destino confirmou a receção de {pt.quantidade}x {pt.peca.nome if pt.peca else ''}.",
            pt.id,
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
