from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import ClassVar

from app.schemas.fatura import EstadoFatura


@dataclass
class Fatura:
    id: int
    numero: str
    ordem_servico_id: int
    loja_id: int
    data_emissao: datetime
    estado: EstadoFatura
    cliente: dict
    trotinete: dict
    servico: dict
    subtotal_pecas: float
    valor_final: float
    pecas_aplicadas: list = field(default_factory=list)


class MockFaturaRepository:
    _data: ClassVar[list[Fatura]] = []
    _next_id: ClassVar[int] = 1

    def get_by_id(self, fatura_id: int) -> Fatura | None:
        return next((f for f in self._data if f.id == fatura_id), None)

    def list(
        self,
        loja_id: int | None,
        ordem_servico_id: int | None,
        data_inicio,
        data_fim,
        page: int,
        page_size: int,
    ) -> tuple[list[Fatura], int]:
        itens = list(self._data)
        if loja_id is not None:
            itens = [f for f in itens if f.loja_id == loja_id]
        if ordem_servico_id is not None:
            itens = [f for f in itens if f.ordem_servico_id == ordem_servico_id]
        if data_inicio is not None:
            itens = [f for f in itens if f.data_emissao.date() >= data_inicio]
        if data_fim is not None:
            itens = [f for f in itens if f.data_emissao.date() <= data_fim]
        total = len(itens)
        start = (page - 1) * page_size
        return itens[start : start + page_size], total

    def list_all(self) -> list[Fatura]:
        return list(self._data)

    def create(
        self,
        ordem_servico_id: int,
        loja_id: int,
        cliente: dict,
        trotinete: dict,
        servico: dict,
        pecas_aplicadas: list,
        subtotal_pecas: float,
        valor_final: float,
    ) -> Fatura:
        nova = Fatura(
            id=self._next_id,
            numero=f"FAT-2026-{self._next_id:04d}",
            ordem_servico_id=ordem_servico_id,
            loja_id=loja_id,
            data_emissao=datetime.now(timezone.utc),
            estado=EstadoFatura.EMITIDA,
            cliente=cliente,
            trotinete=trotinete,
            servico=servico,
            pecas_aplicadas=pecas_aplicadas,
            subtotal_pecas=subtotal_pecas,
            valor_final=valor_final,
        )
        self._data.append(nova)
        type(self)._next_id += 1
        return nova
