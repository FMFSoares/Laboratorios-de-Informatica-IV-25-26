from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SalarioUtilizador(BaseModel):
    id: int
    nome: str
    perfil: str
    loja_id: int | None
    loja_nome: str | None
    salario_base: float
    comissao_percentagem: int | None
    comissao_ganha: float
    total: float

    model_config = ConfigDict(from_attributes=True)
