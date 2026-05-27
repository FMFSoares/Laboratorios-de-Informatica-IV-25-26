from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.schemas.utilizador import PerfilUtilizador


class Utilizador(Base):
    __tablename__ = "utilizadores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[PerfilUtilizador]
    loja_id: Mapped[int | None] = mapped_column(ForeignKey("lojas.id"))
    ativo: Mapped[bool] = mapped_column(default=True)
    comissao: Mapped[int | None]
    salario_base: Mapped[float | None]

    # Relacionamentos
    loja: Mapped["Loja"] = relationship(back_populates="utilizadores")
    ordens_mecanico: Mapped[list["OrdemServico"]] = relationship(back_populates="mecanico")
    auditorias: Mapped[list["Auditoria"]] = relationship(back_populates="utilizador")