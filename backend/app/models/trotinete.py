from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Trotinete(Base):
    __tablename__ = "trotinetes"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    marca: Mapped[str] = mapped_column(String(100))
    modelo: Mapped[str] = mapped_column(String(100))
    numero_serie: Mapped[str] = mapped_column(String(100), unique=True)
    ano_compra: Mapped[int | None]
    cor: Mapped[str | None] = mapped_column(String(50))
    observacoes_tecnicas: Mapped[str | None] = mapped_column(String(500))
    data_registo: Mapped[datetime]

    # Relacionamentos
    cliente: Mapped["Cliente"] = relationship(back_populates="trotinetes")
    ordens_servico: Mapped[list["OrdemServico"]] = relationship(back_populates="trotinete", cascade="all, delete-orphan")