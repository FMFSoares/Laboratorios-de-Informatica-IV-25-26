from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.schemas.ordem_servico import EstadoOrdemServico, PrioridadeOrdemServico


class OrdemServico(Base):
    __tablename__ = "ordens_servico"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    trotinete_id: Mapped[int] = mapped_column(ForeignKey("trotinetes.id"))
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    loja_id: Mapped[int] = mapped_column(ForeignKey("lojas.id"))
    mecanico_id: Mapped[int | None] = mapped_column(ForeignKey("utilizadores.id"))
    estado: Mapped[EstadoOrdemServico]
    prioridade: Mapped[PrioridadeOrdemServico]
    descricao_problema: Mapped[str] = mapped_column(String(1000))
    preco_servico: Mapped[float]
    data_entrada: Mapped[datetime]
    data_conclusao: Mapped[datetime | None]
    tempo_total_minutos: Mapped[int | None]

    # Relacionamentos
    loja: Mapped["Loja"] = relationship(back_populates="ordens_servico")
    cliente: Mapped["Cliente"] = relationship(back_populates="ordens_servico")
    trotinete: Mapped["Trotinete"] = relationship(back_populates="ordens_servico")
    mecanico: Mapped["Utilizador"] = relationship(back_populates="ordens_mecanico")
    pecas_aplicadas: Mapped[list["OSPeca"]] = relationship(back_populates="ordem_servico", cascade="all, delete-orphan")
    registos_tempo: Mapped[list["RegistoTempo"]] = relationship(back_populates="ordem_servico", cascade="all, delete-orphan")
    fatura: Mapped[Optional["Fatura"]] = relationship(back_populates="ordem_servico", cascade="all, delete-orphan", single_parent=True)
    observacoes: Mapped[list["OrdemServicoObservacao"]] = relationship(back_populates="ordem_servico", order_by="OrdemServicoObservacao.criado_em", cascade="all, delete-orphan")
    servicos_diagnostico: Mapped[list["OSServico"]] = relationship(back_populates="ordem_servico", cascade="all, delete-orphan")
    pedidos_peca: Mapped[list["PedidoPeca"]] = relationship(foreign_keys="PedidoPeca.ordem_servico_id", cascade="all, delete-orphan")


class OSPeca(Base):
    __tablename__ = "os_pecas"

    id: Mapped[int] = mapped_column(primary_key=True)
    ordem_servico_id: Mapped[int] = mapped_column(ForeignKey("ordens_servico.id"))
    peca_id: Mapped[int] = mapped_column(ForeignKey("pecas.id"))
    quantidade: Mapped[int]
    preco_venda_unitario: Mapped[float]

    # Relacionamentos
    ordem_servico: Mapped["OrdemServico"] = relationship(back_populates="pecas_aplicadas")
    peca: Mapped["Peca"] = relationship(back_populates="os_pecas")


class RegistoTempo(Base):
    __tablename__ = "registos_tempo"

    id: Mapped[int] = mapped_column(primary_key=True)
    ordem_servico_id: Mapped[int] = mapped_column(ForeignKey("ordens_servico.id"))
    inicio: Mapped[datetime]
    fim: Mapped[datetime | None]
    minutos_esta_sessao: Mapped[int | None]
    tempo_total_acumulado_minutos: Mapped[int | None]
    mecanico_id: Mapped[int | None] = mapped_column(ForeignKey("utilizadores.id"))
    mecanico: Mapped[Optional["Utilizador"]] = relationship()

    # Relacionamentos
    ordem_servico: Mapped["OrdemServico"] = relationship(back_populates="registos_tempo")


class OrdemServicoObservacao(Base):
    __tablename__ = "os_observacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    ordem_servico_id: Mapped[int] = mapped_column(ForeignKey("ordens_servico.id"))
    autor_id: Mapped[int] = mapped_column(ForeignKey("utilizadores.id"))
    texto: Mapped[str] = mapped_column(String(1000))
    criado_em: Mapped[datetime]

    ordem_servico: Mapped["OrdemServico"] = relationship(back_populates="observacoes")
    autor: Mapped["Utilizador"] = relationship()