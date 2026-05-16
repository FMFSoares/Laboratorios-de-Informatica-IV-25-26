from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.schemas.notificacao import TipoNotificacao


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    utilizador_id: Mapped[int] = mapped_column(ForeignKey("utilizadores.id"))
    tipo: Mapped[TipoNotificacao]
    titulo: Mapped[str] = mapped_column(String(200))
    mensagem: Mapped[str] = mapped_column(String(1000))
    lida: Mapped[bool] = mapped_column(default=False)
    data_criacao: Mapped[datetime]
    referencia_id: Mapped[Optional[int]]
    referencia_tipo: Mapped[Optional[str]] = mapped_column(String(50))

    utilizador: Mapped[Optional["Utilizador"]] = relationship()
