from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from app.schemas.utilizador import PerfilUtilizador


@dataclass
class Utilizador:
    id: int
    nome: str
    email: str
    password_hash: str
    perfil: PerfilUtilizador
    loja_id: int | None
    loja_nome: str | None
    ativo: bool


class MockUtilizadorRepository:
    _data: ClassVar[list[Utilizador]] = [
        Utilizador(
            id=1,
            nome="Admin DLMCare",
            email="admin@dlmcare.pt",
            password_hash="$2b$12$AhecmMsG0tcCWLwSSs0yu.KiMnReryFW6v/GLxTBtRbM.AmST1Ez6",
            perfil=PerfilUtilizador.ADMINISTRADOR,
            loja_id=None,
            loja_nome=None,
            ativo=True,
        ),
        Utilizador(
            id=2,
            nome="Gerente Porto",
            email="gerente.porto@dlmcare.pt",
            password_hash="$2b$12$JjmAMgoV2X24aNEFTrKatONRBiugcAB4nHDcO56o6iZy9MGyW1uze",
            perfil=PerfilUtilizador.GERENTE_LOJA,
            loja_id=1,
            loja_nome="DLMCare Porto",
            ativo=True,
        ),
        Utilizador(
            id=3,
            nome="Ana Rececionista",
            email="ana.lisboa@dlmcare.pt",
            password_hash="$2b$12$Q6/Xe4M6ULeAMKigwgPnUeUnQihPItPpYnZLkIW9UG2lb19CriInm",
            perfil=PerfilUtilizador.RECECIONISTA,
            loja_id=1,
            loja_nome="DLMCare Porto",
            ativo=True,
        ),
        Utilizador(
            id=4,
            nome="João Mecânico",
            email="joao.mecanico@dlmcare.pt",
            password_hash="$2b$12$vb7gBO55HoBkVSD5psUumuYhLzjPJe4a1kEK.Bm18783xwiYevcaG",
            perfil=PerfilUtilizador.MECANICO,
            loja_id=1,
            loja_nome="DLMCare Porto",
            ativo=True,
        ),
    ]
    _next_id: ClassVar[int] = 5

    def get_by_id(self, utilizador_id: int) -> Utilizador | None:
        return next((u for u in self._data if u.id == utilizador_id), None)

    def get_by_email(self, email: str) -> Utilizador | None:
        email_lower = email.lower()
        return next((u for u in self._data if u.email.lower() == email_lower), None)

    def list(self, page: int, page_size: int) -> tuple[list[Utilizador], int]:
        total = len(self._data)
        start = (page - 1) * page_size
        return self._data[start : start + page_size], total

    def list_by_perfil(self, perfil: PerfilUtilizador, loja_id: int | None = None) -> list[Utilizador]:
        itens = [u for u in self._data if u.perfil == perfil]
        if loja_id is not None:
            itens = [u for u in itens if u.loja_id == loja_id]
        return itens

    def list_all(self) -> list[Utilizador]:
        return list(self._data)

    def exists_email(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def create(
        self,
        nome: str,
        email: str,
        password_hash: str,
        perfil: PerfilUtilizador,
        loja_id: int | None,
        loja_nome: str | None,
        ativo: bool,
    ) -> Utilizador:
        novo = Utilizador(
            id=self._next_id,
            nome=nome,
            email=email,
            password_hash=password_hash,
            perfil=perfil,
            loja_id=loja_id,
            loja_nome=loja_nome,
            ativo=ativo,
        )
        self._data.append(novo)
        type(self)._next_id += 1
        return novo
