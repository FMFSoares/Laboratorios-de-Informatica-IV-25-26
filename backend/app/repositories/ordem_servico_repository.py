from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import ClassVar

from app.schemas.ordem_servico import EstadoOrdemServico as E, PrioridadeOrdemServico


@dataclass
class OrdemServico:
    id: int
    numero: str
    trotinete_id: int
    cliente_id: int
    loja_id: int
    estado: E
    prioridade: PrioridadeOrdemServico
    descricao_problema: str
    preco_servico: float
    data_entrada: datetime
    mecanico_id: int | None = None
    data_conclusao: datetime | None = None
    pecas_aplicadas: list = field(default_factory=list)
    observacoes: list = field(default_factory=list)
    tempo_total_minutos: int | None = None
    inicio_tempo_atual: datetime | None = None
    fatura_id: int | None = None


class MockOrdemServicoRepository:
    _data: ClassVar[list[OrdemServico]] = [
        OrdemServico(
            id=1,
            numero="OS-2026-0001",
            trotinete_id=1,
            cliente_id=1,
            loja_id=1,
            mecanico_id=4,
            estado=E.PENDENTE,
            prioridade=PrioridadeOrdemServico.NORMAL,
            descricao_problema="Não arranca. Bateria parece descarregada mesmo após carga.",
            preco_servico=25.00,
            data_entrada=datetime(2026, 4, 28, 9, 0, tzinfo=timezone.utc),
        ),
        OrdemServico(
            id=2,
            numero="OS-2026-0002",
            trotinete_id=2,
            cliente_id=2,
            loja_id=1,
            mecanico_id=4,
            estado=E.EM_REPARACAO,
            prioridade=PrioridadeOrdemServico.ALTA,
            descricao_problema="Pneu traseiro furado.",
            preco_servico=15.00,
            data_entrada=datetime(2026, 4, 25, 10, 0, tzinfo=timezone.utc),
            pecas_aplicadas=[
                {
                    "peca_id": 2,
                    "peca_nome": "Pneu Traseiro 8.5x2 Xiaomi",
                    "quantidade": 1,
                    "preco_venda_unitario": 18.90,
                    "subtotal": 18.90,
                }
            ],
            tempo_total_minutos=30,
        ),
    ]
    _next_id: ClassVar[int] = 3
    _next_obs_id: ClassVar[int] = 1

    def get_by_id(self, os_id: int) -> OrdemServico | None:
        return next((o for o in self._data if o.id == os_id), None)

    def list(
        self,
        loja_id: int | None,
        estado: E | None,
        mecanico_id: int | None,
        data_inicio,
        data_fim,
        page: int,
        page_size: int,
    ) -> tuple[list[OrdemServico], int]:
        itens = list(self._data)
        if loja_id is not None:
            itens = [o for o in itens if o.loja_id == loja_id]
        if estado is not None:
            itens = [o for o in itens if o.estado == estado]
        if mecanico_id is not None:
            itens = [o for o in itens if o.mecanico_id == mecanico_id]
        if data_inicio is not None:
            itens = [o for o in itens if o.data_entrada.date() >= data_inicio]
        if data_fim is not None:
            itens = [o for o in itens if o.data_entrada.date() <= data_fim]
        total = len(itens)
        start = (page - 1) * page_size
        return itens[start : start + page_size], total

    def list_all(self) -> list[OrdemServico]:
        return list(self._data)

    def list_by_mecanico(self, mecanico_id: int) -> list[OrdemServico]:
        return [o for o in self._data if o.mecanico_id == mecanico_id]

    def count_by_trotinete(self, trotinete_id: int) -> int:
        return sum(1 for o in self._data if o.trotinete_id == trotinete_id)

    def create(
        self,
        trotinete_id: int,
        cliente_id: int,
        loja_id: int,
        mecanico_id: int | None,
        estado: E,
        prioridade: PrioridadeOrdemServico,
        descricao_problema: str,
        preco_servico: float,
    ) -> OrdemServico:
        nova = OrdemServico(
            id=self._next_id,
            numero=f"OS-2026-{self._next_id:04d}",
            trotinete_id=trotinete_id,
            cliente_id=cliente_id,
            loja_id=loja_id,
            mecanico_id=mecanico_id,
            estado=estado,
            prioridade=prioridade,
            descricao_problema=descricao_problema,
            preco_servico=preco_servico,
            data_entrada=datetime.now(timezone.utc),
        )
        self._data.append(nova)
        type(self)._next_id += 1
        return nova

    def adicionar_observacao(self, os_id: int, texto: str, autor_id: int, autor_nome: str) -> dict:
        os = self.get_by_id(os_id)
        obs = {
            "id": type(self)._next_obs_id,
            "texto": texto,
            "autor_id": autor_id,
            "autor_nome": autor_nome,
            "criado_em": datetime.now(timezone.utc),
        }
        os.observacoes.append(obs)
        type(self)._next_obs_id += 1
        return obs
