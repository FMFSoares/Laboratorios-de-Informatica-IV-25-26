from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Loja:
    id: int
    nome: str
    cidade: str
    morada: str
    telefone: str
    email: str
    ativo: bool


class MockLojaRepository:
    _data: ClassVar[list[Loja]] = [
        Loja(
            id=1,
            nome="DLMCare Porto",
            cidade="Porto",
            morada="Rua de Santa Catarina 100, 4000-447 Porto",
            telefone="222000001",
            email="porto@dlmcare.pt",
            ativo=True,
        ),
        Loja(
            id=2,
            nome="DLMCare Lisboa",
            cidade="Lisboa",
            morada="Av. da Liberdade 100, 1250-096 Lisboa",
            telefone="213000001",
            email="lisboa@dlmcare.pt",
            ativo=True,
        ),
    ]

    def get_by_id(self, loja_id: int) -> Loja | None:
        return next((l for l in self._data if l.id == loja_id), None)

    def list(self, loja_id_filtro: int | None = None) -> list[Loja]:
        if loja_id_filtro is not None:
            return [l for l in self._data if l.id == loja_id_filtro]
        return list(self._data)

    def exists(self, loja_id: int) -> bool:
        return self.get_by_id(loja_id) is not None

    def get_nome(self, loja_id: int) -> str | None:
        loja = self.get_by_id(loja_id)
        return loja.nome if loja else None

    def get_telefone(self, loja_id: int) -> str | None:
        loja = self.get_by_id(loja_id)
        return loja.telefone if loja else None

    def as_dict(self, loja_id: int) -> dict | None:
        loja = self.get_by_id(loja_id)
        if loja is None:
            return None
        return {
            "nome": loja.nome,
            "morada": loja.morada,
            "telefone": loja.telefone,
        }
