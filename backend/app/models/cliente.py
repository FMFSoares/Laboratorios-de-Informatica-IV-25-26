from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    nif: Mapped[str] = mapped_column(String(9), unique=True)
    telemovel: Mapped[str] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    morada: Mapped[str | None] = mapped_column(String(255))
    consentimento_rgpd: Mapped[bool] = mapped_column(default=False)
    data_registo: Mapped[datetime]
    loja_id: Mapped[int] = mapped_column(ForeignKey("lojas.id"))

    loja: Mapped["Loja"] = relationship(back_populates="clientes")
    trotinetes: Mapped[list["Trotinete"]] = relationship(back_populates="cliente")
    ordens_servico: Mapped[list["OrdemServico"]] = relationship(back_populates="cliente")