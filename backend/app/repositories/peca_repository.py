from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from app.schemas.peca import CategoriaPeca


@dataclass
class Peca:
    id: int
    referencia: str
    nome: str
    categoria: CategoriaPeca
    unidade: str
    preco_custo: float
    preco_venda: float
    ativo: bool
    descricao: str | None = None


class MockPecaRepository:
    _data: ClassVar[list[Peca]] = [
        Peca(
            id=1,
            referencia="PEC-BAT-001",
            nome="Bateria 36V 7.5Ah Xiaomi",
            categoria=CategoriaPeca.BATERIA,
            descricao="Bateria de substituição compatível com Xiaomi M365 e Pro.",
            unidade="unidade",
            preco_custo=42.00,
            preco_venda=89.90,
            ativo=True,
        ),
        Peca(
            id=2,
            referencia="PEC-PNE-001",
            nome="Pneu Traseiro 8.5x2 Xiaomi",
            categoria=CategoriaPeca.PNEU,
            descricao="Pneu anti-furo para trotinetes Xiaomi e compatíveis.",
            unidade="unidade",
            preco_custo=8.50,
            preco_venda=18.90,
            ativo=True,
        ),
        Peca(
            id=3,
            referencia="PEC-TRA-001",
            nome="Pastilhas de Travão Ninebot",
            categoria=CategoriaPeca.TRAVAO,
            descricao="Kit de pastilhas para travões de disco Ninebot.",
            unidade="par",
            preco_custo=5.00,
            preco_venda=12.50,
            ativo=True,
        ),
        Peca(
            id=4,
            referencia="PEC-MOT-001",
            nome="Motor Hub 250W",
            categoria=CategoriaPeca.MOTOR,
            descricao="Motor de substituição 250W compatível com múltiplas marcas.",
            unidade="unidade",
            preco_custo=95.00,
            preco_venda=195.00,
            ativo=True,
        ),
    ]
    _next_id: ClassVar[int] = 5

    def get_by_id(self, peca_id: int) -> Peca | None:
        return next((p for p in self._data if p.id == peca_id), None)

    def list(
        self,
        query: str | None,
        categoria: CategoriaPeca | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Peca], int]:
        itens = [p for p in self._data if p.ativo]
        if categoria:
            itens = [p for p in itens if p.categoria == categoria]
        if query:
            q = query.lower()
            itens = [p for p in itens if q in p.nome.lower() or q in p.referencia.lower()]
        total = len(itens)
        start = (page - 1) * page_size
        return itens[start : start + page_size], total

    def list_all(self) -> list[Peca]:
        return list(self._data)

    def exists_referencia(self, referencia: str) -> bool:
        return any(p.referencia == referencia for p in self._data)

    def create(
        self,
        referencia: str,
        nome: str,
        categoria: CategoriaPeca,
        descricao: str | None,
        unidade: str,
        preco_custo: float,
        preco_venda: float,
    ) -> Peca:
        nova = Peca(
            id=self._next_id,
            referencia=referencia,
            nome=nome,
            categoria=categoria,
            descricao=descricao,
            unidade=unidade,
            preco_custo=preco_custo,
            preco_venda=preco_venda,
            ativo=True,
        )
        self._data.append(nova)
        type(self)._next_id += 1
        return nova
