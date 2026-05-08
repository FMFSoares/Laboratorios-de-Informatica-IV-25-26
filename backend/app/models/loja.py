from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Loja(Base):
    __tablename__ = "lojas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    cidade: Mapped[str] = mapped_column(String(100))
    morada: Mapped[str] = mapped_column(String(255))
    telefone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    ativo: Mapped[bool] = mapped_column(default=True)

    # Relacionamentos
    utilizadores: Mapped[list["Utilizador"]] = relationship(back_populates="loja")
    clientes: Mapped[list["Cliente"]] = relationship(back_populates="loja")
    stock: Mapped[list["StockLoja"]] = relationship(back_populates="loja")
    ordens_servico: Mapped[list["OrdemServico"]] = relationship(back_populates="loja")
    auditorias: Mapped[list["Auditoria"]] = relationship(back_populates="loja")