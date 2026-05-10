from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import ClassVar


@dataclass
class Trotinete:
    id: int
    cliente_id: int
    loja_id: int
    marca: str
    modelo: str
    numero_serie: str
    data_registo: datetime
    ano_compra: int | None = None
    cor: str | None = None
    observacoes_tecnicas: str | None = None


class MockTrotineteRepository:
    _data: ClassVar[list[Trotinete]] = [
        Trotinete(
            id=1,
            cliente_id=1,
            loja_id=1,
            marca="Xiaomi",
            modelo="Mi Electric Scooter 3",
            numero_serie="XM2024ABC123",
            ano_compra=2024,
            cor="Preto",
            observacoes_tecnicas="Bateria substituída em 2025. Controlador original.",
            data_registo=datetime(2026, 4, 10, 9, 0, tzinfo=timezone.utc),
        ),
        Trotinete(
            id=2,
            cliente_id=2,
            loja_id=1,
            marca="Ninebot",
            modelo="E45E",
            numero_serie="NB2023XYZ456",
            ano_compra=2023,
            cor="Cinzento",
            observacoes_tecnicas=None,
            data_registo=datetime(2026, 4, 12, 11, 30, tzinfo=timezone.utc),
        ),
    ]
    _next_id: ClassVar[int] = 3

    def get_by_id(self, trotinete_id: int) -> Trotinete | None:
        return next((t for t in self._data if t.id == trotinete_id), None)

    def list(
        self,
        loja_id: int | None,
        cliente_id: int | None,
        numero_serie: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Trotinete], int]:
        itens = list(self._data)
        if loja_id is not None:
            itens = [t for t in itens if t.loja_id == loja_id]
        if cliente_id is not None:
            itens = [t for t in itens if t.cliente_id == cliente_id]
        if numero_serie:
            itens = [t for t in itens if t.numero_serie == numero_serie]
        total = len(itens)
        start = (page - 1) * page_size
        return itens[start : start + page_size], total

    def list_by_cliente(self, cliente_id: int) -> list[Trotinete]:
        return [t for t in self._data if t.cliente_id == cliente_id]

    def exists_numero_serie(self, numero_serie: str) -> bool:
        return any(t.numero_serie == numero_serie for t in self._data)

    def count_by_trotinete(self, trotinete_id: int) -> int:
        """Used to compute total_ordens on scooter detail. Delegated from OS repo to avoid circular deps."""
        from app.repositories.ordem_servico_repository import MockOrdemServicoRepository
        os_repo = MockOrdemServicoRepository()
        return os_repo.count_by_trotinete(trotinete_id)

    def create(
        self,
        cliente_id: int,
        loja_id: int,
        marca: str,
        modelo: str,
        numero_serie: str,
        ano_compra: int | None,
        cor: str | None,
        observacoes_tecnicas: str | None,
    ) -> Trotinete:
        nova = Trotinete(
            id=self._next_id,
            cliente_id=cliente_id,
            loja_id=loja_id,
            marca=marca,
            modelo=modelo,
            numero_serie=numero_serie,
            ano_compra=ano_compra,
            cor=cor,
            observacoes_tecnicas=observacoes_tecnicas,
            data_registo=datetime.now(timezone.utc),
        )
        self._data.append(nova)
        type(self)._next_id += 1
        return nova
