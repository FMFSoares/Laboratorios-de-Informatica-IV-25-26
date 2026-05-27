from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ServicoCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    preco_base: float = Field(..., ge=0.0)
    ativo: bool = True

    model_config = ConfigDict(
        json_schema_extra={"example": {"nome": "Revisão geral", "preco_base": 35.00, "ativo": True}}
    )


class ServicoUpdate(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=200)
    preco_base: float | None = Field(None, ge=0.0)
    ativo: bool | None = None


class ServicoResponse(BaseModel):
    id: int
    nome: str
    preco_base: float
    ativo: bool

    model_config = ConfigDict(from_attributes=True)
