from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.schemas.auditoria import TipoEventoAuditoria


class Auditoria(Base):
    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento: Mapped[TipoEventoAuditoria]
    descricao: Mapped[str] = mapped_column(String(255))
    utilizador_id: Mapped[int | None] = mapped_column(ForeignKey("utilizadores.id"))
    loja_id: Mapped[int | None] = mapped_column(ForeignKey("lojas.id"))
    ip_origem: Mapped[str | None] = mapped_column(String(50))
    timestamp: Mapped[datetime]
    detalhe: Mapped[dict] = mapped_column(JSON)

    utilizador: Mapped["Utilizador"] = relationship(back_populates="auditorias")
    loja: Mapped["Loja"] = relationship(back_populates="auditorias")