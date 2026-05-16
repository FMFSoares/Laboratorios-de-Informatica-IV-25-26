from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.schemas.transferencia import EstadoPedidoTransferencia, EstadoPedidoPeca


class PedidoTransferencia(Base):
    __tablename__ = "pedidos_transferencia"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    loja_origem_id: Mapped[int] = mapped_column(ForeignKey("lojas.id"))
    loja_destino_id: Mapped[int] = mapped_column(ForeignKey("lojas.id"))
    gerente_origem_id: Mapped[int] = mapped_column(ForeignKey("utilizadores.id"))
    gerente_destino_id: Mapped[int] = mapped_column(ForeignKey("utilizadores.id"))
    peca_id: Mapped[int] = mapped_column(ForeignKey("pecas.id"))
    quantidade: Mapped[int]
    estado: Mapped[EstadoPedidoTransferencia]
    data_pedido: Mapped[datetime]
    data_resposta: Mapped[Optional[datetime]]
    data_recepcao: Mapped[Optional[datetime]]
    data_assinatura_origem: Mapped[Optional[datetime]]
    data_assinatura_destino: Mapped[Optional[datetime]]
    observacoes_pedido: Mapped[Optional[str]] = mapped_column(String(500))
    observacoes_resposta: Mapped[Optional[str]] = mapped_column(String(500))

    loja_origem: Mapped[Optional["Loja"]] = relationship(foreign_keys=[loja_origem_id])
    loja_destino: Mapped[Optional["Loja"]] = relationship(foreign_keys=[loja_destino_id])
    gerente_origem: Mapped[Optional["Utilizador"]] = relationship(foreign_keys=[gerente_origem_id])
    gerente_destino: Mapped[Optional["Utilizador"]] = relationship(foreign_keys=[gerente_destino_id])
    peca: Mapped[Optional["Peca"]] = relationship()


class PedidoPeca(Base):
    __tablename__ = "pedidos_peca"

    id: Mapped[int] = mapped_column(primary_key=True)
    ordem_servico_id: Mapped[int] = mapped_column(ForeignKey("ordens_servico.id"))
    mecanico_id: Mapped[int] = mapped_column(ForeignKey("utilizadores.id"))
    loja_id: Mapped[int] = mapped_column(ForeignKey("lojas.id"))
    peca_id: Mapped[int] = mapped_column(ForeignKey("pecas.id"))
    quantidade: Mapped[int]
    estado: Mapped[EstadoPedidoPeca]
    data_pedido: Mapped[datetime]
    data_resposta: Mapped[Optional[datetime]]
    observacoes: Mapped[Optional[str]] = mapped_column(String(500))

    ordem_servico: Mapped[Optional["OrdemServico"]] = relationship(foreign_keys=[ordem_servico_id])
    mecanico: Mapped[Optional["Utilizador"]] = relationship(foreign_keys=[mecanico_id])
    loja: Mapped[Optional["Loja"]] = relationship(foreign_keys=[loja_id])
    peca: Mapped[Optional["Peca"]] = relationship(foreign_keys=[peca_id])
