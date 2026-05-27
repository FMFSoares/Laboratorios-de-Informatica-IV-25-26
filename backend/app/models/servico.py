from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Servico(Base):
    __tablename__ = "servicos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200))
    preco_base: Mapped[float]
    ativo: Mapped[bool] = mapped_column(default=True)


class OSServico(Base):
    __tablename__ = "os_servicos"

    id: Mapped[int] = mapped_column(primary_key=True)
    ordem_servico_id: Mapped[int] = mapped_column(ForeignKey("ordens_servico.id"))
    servico_id: Mapped[int | None] = mapped_column(ForeignKey("servicos.id"), nullable=True)
    nome: Mapped[str] = mapped_column(String(200))
    preco: Mapped[float]

    ordem_servico: Mapped["OrdemServico"] = relationship(back_populates="servicos_diagnostico")
    servico: Mapped[Optional["Servico"]] = relationship()
