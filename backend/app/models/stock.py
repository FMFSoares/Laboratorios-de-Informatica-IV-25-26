from __future__ import annotations

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StockLoja(Base):
    __tablename__ = "stock_lojas"

    __table_args__ = (UniqueConstraint('peca_id', 'loja_id', name='uq_stock_peca_loja'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    peca_id: Mapped[int] = mapped_column(ForeignKey("pecas.id"))
    loja_id: Mapped[int] = mapped_column(ForeignKey("lojas.id"))
    quantidade: Mapped[int] = mapped_column(default=0)
    limite_minimo: Mapped[int] = mapped_column(default=0)

    # Relacionamentos
    peca: Mapped["Peca"] = relationship(back_populates="stock_lojas")
    loja: Mapped["Loja"] = relationship(back_populates="stock")