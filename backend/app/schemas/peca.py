from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# ── Enum: categorias de peça ──────────────────────────────────────────────────


class CategoriaPeca(str, Enum):
    BATERIA = "BATERIA"
    PNEU = "PNEU"
    TRAVAO = "TRAVAO"
    MOTOR = "MOTOR"
    CONTROLADOR = "CONTROLADOR"
    LUZ = "LUZ"
    ACESSORIO = "ACESSORIO"
    OUTRO = "OUTRO"


# ── Schema de criação ─────────────────────────────────────────────────────────


class PecaCreate(BaseModel):
    """
    Body do POST /api/v1/pecas.

    Ambos os preços são recebidos na criação:
    - preco_custo: valor interno de aquisição (nunca exposto ao cliente).
    - preco_venda: valor cobrado ao cliente na fatura.
    """

    referencia: str = Field(..., min_length=1, description="Referência única da peça.")
    nome: str = Field(..., min_length=1, description="Nome descritivo da peça.")
    categoria: CategoriaPeca = Field(..., description="Categoria da peça.")
    descricao: str | None = Field(None, description="Descrição técnica detalhada.")
    unidade: str = Field("unidade", description="Unidade de medida (ex: unidade, metro).")
    preco_custo: float = Field(
        ...,
        ge=0.0,
        description="Preço de custo interno (aquisição). Nunca usado no cálculo da fatura.",
    )
    preco_venda: float = Field(
        ...,
        ge=0.0,
        description="Preço de venda cobrado ao cliente. Usado no cálculo da fatura.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "referencia": "PEC-BAT-001",
                "nome": "Bateria 36V 7.5Ah Xiaomi",
                "categoria": "BATERIA",
                "descricao": "Bateria de substituição compatível com Xiaomi M365 e Pro.",
                "unidade": "unidade",
                "preco_custo": 42.00,
                "preco_venda": 89.90,
            }
        }
    )


# ── Schema de resposta público (sem preco_custo) ──────────────────────────────


class PecaResponse(BaseModel):
    """
    Resposta pública de uma peça.
    preco_custo é OMITIDO — é informação interna de gestão.
    """

    id: int
    referencia: str
    nome: str
    categoria: CategoriaPeca
    descricao: str | None
    unidade: str
    preco_venda: float = Field(
        ..., description="Preço de venda cobrado ao cliente."
    )
    ativo: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "referencia": "PEC-BAT-001",
                "nome": "Bateria 36V 7.5Ah Xiaomi",
                "categoria": "BATERIA",
                "descricao": "Bateria de substituição compatível com Xiaomi M365 e Pro.",
                "unidade": "unidade",
                "preco_venda": 89.90,
                "ativo": True,
            }
        },
    )


class PecaUpdate(BaseModel):
    """Body do PATCH /pecas/{id} — todos os campos opcionais. Referência não é editável."""
    nome: str | None = Field(None, min_length=1)
    categoria: CategoriaPeca | None = None
    descricao: str | None = None
    unidade: str | None = None
    preco_custo: float | None = Field(None, ge=0.0)
    preco_venda: float | None = Field(None, ge=0.0)
    ativo: bool | None = None


class PecaDetalheResponse(PecaResponse):
    """
    Resposta de detalhe de uma peça — inclui preco_custo para uso interno (admin/gerente).
    """
    preco_custo: float | None = None


class PecaResumo(BaseModel):
    """Versão mínima para respostas aninhadas (ex: stock, OS)."""

    id: int
    referencia: str
    nome: str
    categoria: CategoriaPeca
    preco_venda: float

    model_config = ConfigDict(from_attributes=True)
