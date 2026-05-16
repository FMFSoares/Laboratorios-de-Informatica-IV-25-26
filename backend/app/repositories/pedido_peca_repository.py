from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

from app.models.transferencia import PedidoPeca
from app.schemas.transferencia import EstadoPedidoPeca


class PedidoPecaRepository:
    def __init__(self, db: Session):
        self.db = db

    def _base_query(self):
        return self.db.query(PedidoPeca).options(
            joinedload(PedidoPeca.peca),
            joinedload(PedidoPeca.ordem_servico),
            joinedload(PedidoPeca.mecanico),
            joinedload(PedidoPeca.loja),
        )

    def create(self, **kwargs) -> PedidoPeca:
        pp = PedidoPeca(**kwargs)
        self.db.add(pp)
        return pp

    def get_by_id(self, pp_id: int) -> PedidoPeca | None:
        return self._base_query().filter(PedidoPeca.id == pp_id).first()

    def list_by_loja(
        self, loja_id: int, estado: EstadoPedidoPeca | None, skip: int, limit: int
    ) -> tuple[list[PedidoPeca], int]:
        query = self._base_query().filter(PedidoPeca.loja_id == loja_id)
        if estado is not None:
            query = query.filter(PedidoPeca.estado == estado)
        total = query.count()
        itens = query.order_by(PedidoPeca.data_pedido.desc()).offset(skip).limit(limit).all()
        return itens, total

    def list_by_mecanico(
        self, mecanico_id: int, skip: int, limit: int
    ) -> tuple[list[PedidoPeca], int]:
        query = self._base_query().filter(PedidoPeca.mecanico_id == mecanico_id)
        total = query.count()
        itens = query.order_by(PedidoPeca.data_pedido.desc()).offset(skip).limit(limit).all()
        return itens, total
