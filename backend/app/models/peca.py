from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.schemas.peca import CategoriaPeca


class Peca(Base):
    __tablename__ = "pecas"

    id: Mapped[int] = mapped_column(primary_key=True)
    referencia: Mapped[str] = mapped_column(String(50), unique=True)
    nome: Mapped[str] = mapped_column(String(150))
    categoria: Mapped[CategoriaPeca]
    descricao: Mapped[str | None] = mapped_column(String(500))
    unidade: Mapped[str] = mapped_column(String(50))
    preco_custo: Mapped[float]
    preco_venda: Mapped[float]
    ativo: Mapped[bool] = mapped_column(default=True)

    # Relacionamentos
    stock_lojas: Mapped[list["StockLoja"]] = relationship(back_populates="peca")
    os_pecas: Mapped[list["OSPeca"]] = relationship(back_populates="peca")