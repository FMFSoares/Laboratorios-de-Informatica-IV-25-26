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
        Peca(id=1,  referencia="PEC-BAT-001", nome="Bateria 36V 7.5Ah Xiaomi",          categoria=CategoriaPeca.BATERIA,      unidade="unidade", preco_custo=42.00, preco_venda=89.90,  ativo=True,  descricao="Bateria de substituição compatível com Xiaomi M365 e Pro."),
        Peca(id=2,  referencia="PEC-BAT-002", nome="Bateria 48V 10Ah Ninebot",           categoria=CategoriaPeca.BATERIA,      unidade="unidade", preco_custo=58.00, preco_venda=119.90, ativo=True,  descricao="Bateria de alta capacidade para Ninebot Max G30."),
        Peca(id=3,  referencia="PEC-PNE-001", nome="Pneu Traseiro 8.5x2 Xiaomi",        categoria=CategoriaPeca.PNEU,         unidade="unidade", preco_custo=8.50,  preco_venda=18.90,  ativo=True,  descricao="Pneu anti-furo para trotinetes Xiaomi e compatíveis."),
        Peca(id=4,  referencia="PEC-PNE-002", nome="Pneu Dianteiro 10x2.5 Ninebot",     categoria=CategoriaPeca.PNEU,         unidade="unidade", preco_custo=11.00, preco_venda=24.90,  ativo=True,  descricao="Pneu pneumático dianteiro para Ninebot Max."),
        Peca(id=5,  referencia="PEC-TRA-001", nome="Pastilhas de Travão Ninebot",        categoria=CategoriaPeca.TRAVAO,       unidade="par",     preco_custo=5.00,  preco_venda=12.50,  ativo=True,  descricao="Kit de pastilhas para travões de disco Ninebot."),
        Peca(id=6,  referencia="PEC-TRA-002", nome="Cabo de Travão Universal",           categoria=CategoriaPeca.TRAVAO,       unidade="unidade", preco_custo=3.50,  preco_venda=8.90,   ativo=True,  descricao="Cabo de travão dianteiro/traseiro compatível com a maioria das marcas."),
        Peca(id=7,  referencia="PEC-MOT-001", nome="Motor Hub 250W",                     categoria=CategoriaPeca.MOTOR,        unidade="unidade", preco_custo=95.00, preco_venda=195.00, ativo=True,  descricao="Motor de substituição 250W compatível com múltiplas marcas."),
        Peca(id=8,  referencia="PEC-CTR-001", nome="Controlador ESC Xiaomi M365",        categoria=CategoriaPeca.CONTROLADOR,  unidade="unidade", preco_custo=28.00, preco_venda=59.90,  ativo=True,  descricao="Placa controladora (ESC) de substituição para Xiaomi M365."),
        Peca(id=9,  referencia="PEC-CTR-002", nome="Display BLE Ninebot G30",            categoria=CategoriaPeca.CONTROLADOR,  unidade="unidade", preco_custo=22.00, preco_venda=44.90,  ativo=True,  descricao="Painel de controlo com conectividade Bluetooth para Ninebot G30."),
        Peca(id=10, referencia="PEC-LUZ-001", nome="Farol Dianteiro LED 5W",             categoria=CategoriaPeca.LUZ,          unidade="unidade", preco_custo=6.00,  preco_venda=14.90,  ativo=True,  descricao="Farol LED de substituição, compatível com Xiaomi e Ninebot."),
        Peca(id=11, referencia="PEC-ACS-001", nome="Suporte de Telemóvel Universal",     categoria=CategoriaPeca.ACESSORIO,    unidade="unidade", preco_custo=4.00,  preco_venda=9.90,   ativo=True,  descricao="Suporte articulado compatível com guiadores de 22-26mm."),
        Peca(id=12, referencia="PEC-OUT-001", nome="Kit Parafusos M4 (50 unid.)",        categoria=CategoriaPeca.OUTRO,        unidade="kit",     preco_custo=2.50,  preco_venda=6.50,   ativo=True,  descricao="Conjunto de parafusos M4 inox para reparações gerais."),
    ]
    _next_id: ClassVar[int] = 13

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
