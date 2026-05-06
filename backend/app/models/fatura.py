from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.schemas.fatura import EstadoFatura


class Fatura(Base):
    __tablename__ = "faturas"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(50), unique=True)
    ordem_servico_id: Mapped[int] = mapped_column(ForeignKey("ordens_servico.id"), unique=True)
    data_emissao: Mapped[datetime]
    estado: Mapped[EstadoFatura]
    subtotal_pecas: Mapped[float]
    valor_final: Mapped[float]

    ordem_servico: Mapped["OrdemServico"] = relationship(back_populates="fatura")