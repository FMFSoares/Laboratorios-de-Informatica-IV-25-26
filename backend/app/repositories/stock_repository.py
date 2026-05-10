from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from fastapi import HTTPException, status


@dataclass
class StockItem:
    peca_id: int
    loja_id: int
    quantidade: int
    limite_minimo: int


class MockStockRepository:
    _data: ClassVar[list[StockItem]] = [
        StockItem(peca_id=1, loja_id=1, quantidade=3,  limite_minimo=5),
        StockItem(peca_id=2, loja_id=1, quantidade=12, limite_minimo=3),
        StockItem(peca_id=3, loja_id=1, quantidade=8,  limite_minimo=2),
        StockItem(peca_id=4, loja_id=1, quantidade=2,  limite_minimo=2),
        StockItem(peca_id=1, loja_id=2, quantidade=0,  limite_minimo=3),
        StockItem(peca_id=2, loja_id=2, quantidade=5,  limite_minimo=2),
    ]

    def get(self, peca_id: int, loja_id: int) -> StockItem | None:
        return next(
            (s for s in self._data if s.peca_id == peca_id and s.loja_id == loja_id),
            None,
        )

    def get_or_create(self, peca_id: int, loja_id: int) -> StockItem:
        item = self.get(peca_id, loja_id)
        if item is None:
            item = StockItem(peca_id=peca_id, loja_id=loja_id, quantidade=0, limite_minimo=2)
            self._data.append(item)
        return item

    def list(
        self,
        loja_id: int | None,
        apenas_alertas: bool,
        page: int,
        page_size: int,
    ) -> tuple[list[StockItem], int]:
        itens = list(self._data)
        if loja_id is not None:
            itens = [s for s in itens if s.loja_id == loja_id]
        if apenas_alertas:
            itens = [s for s in itens if s.quantidade <= s.limite_minimo]
        total = len(itens)
        start = (page - 1) * page_size
        return itens[start : start + page_size], total

    def list_all(self) -> list[StockItem]:
        return list(self._data)

    def get_disponivel(self, peca_id: int, loja_id: int) -> int:
        item = self.get(peca_id, loja_id)
        return item.quantidade if item else 0

    def consumir(self, peca_id: int, loja_id: int, quantidade: int) -> None:
        item = self.get(peca_id, loja_id)
        if item is None or item.quantidade < quantidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"detail": "Stock insuficiente.", "code": "INSUFFICIENT_STOCK"},
            )
        item.quantidade -= quantidade

    def adicionar(self, peca_id: int, loja_id: int, quantidade: int) -> StockItem:
        item = self.get_or_create(peca_id, loja_id)
        item.quantidade += quantidade
        return item

    def transferir(self, peca_id: int, loja_origem_id: int, loja_destino_id: int, quantidade: int) -> tuple[StockItem, StockItem]:
        origem = self.get_or_create(peca_id, loja_origem_id)
        if origem.quantidade < quantidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "detail": f"Stock insuficiente na loja de origem (disponível: {origem.quantidade}).",
                    "code": "INSUFFICIENT_STOCK",
                },
            )
        destino = self.get_or_create(peca_id, loja_destino_id)
        origem.quantidade -= quantidade
        destino.quantidade += quantidade
        return origem, destino
