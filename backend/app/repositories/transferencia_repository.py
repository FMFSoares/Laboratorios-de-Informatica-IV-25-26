from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

from app.models.transferencia import PedidoTransferencia
from app.schemas.transferencia import EstadoPedidoTransferencia


class TransferenciaRepository:
    def __init__(self, db: Session):
        self.db = db

    def _base_query(self):
        return self.db.query(PedidoTransferencia).options(
            joinedload(PedidoTransferencia.loja_origem),
            joinedload(PedidoTransferencia.loja_destino),
            joinedload(PedidoTransferencia.gerente_origem),
            joinedload(PedidoTransferencia.gerente_destino),
            joinedload(PedidoTransferencia.peca),
        )

    def create(self, **kwargs) -> PedidoTransferencia:
        from datetime import datetime, timezone
        pt = PedidoTransferencia(**kwargs)
        self.db.add(pt)
        self.db.flush()
        pt.numero = f"TRF-{datetime.now(timezone.utc).year}-{pt.id:04d}"
        return pt

    def get_by_id(self, pt_id: int) -> PedidoTransferencia | None:
        return self._base_query().filter(PedidoTransferencia.id == pt_id).first()

    def list(
        self,
        loja_id: int | None,
        estado: EstadoPedidoTransferencia | None,
        skip: int,
        limit: int,
    ) -> tuple[list[PedidoTransferencia], int]:
        query = self._base_query()
        if loja_id is not None:
            query = query.filter(
                (PedidoTransferencia.loja_origem_id == loja_id)
                | (PedidoTransferencia.loja_destino_id == loja_id)
            )
        if estado is not None:
            query = query.filter(PedidoTransferencia.estado == estado)
        total = query.count()
        itens = query.order_by(PedidoTransferencia.data_pedido.desc()).offset(skip).limit(limit).all()
        return itens, total
