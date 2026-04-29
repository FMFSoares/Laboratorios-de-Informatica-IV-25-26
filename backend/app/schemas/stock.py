from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ── Enum: tipos de movimento de stock ────────────────────────────────────────


class TipoMovimentoStock(str, Enum):
    ENTRADA = "ENTRADA"
    TRANSFERENCIA = "TRANSFERENCIA"
    SAIDA_REPARACAO = "SAIDA_REPARACAO"


# ── Schema de consulta de stock ───────────────────────────────────────────────


class StockItemResponse(BaseModel):
    """
    Resposta de um item de stock (GET /api/v1/stock).
    O campo alerta é True quando quantidade <= limite_minimo.
    """

    peca_id: int
    peca_referencia: str
    peca_nome: str
    loja_id: int
    loja_nome: str
    quantidade: int = Field(..., ge=0, description="Quantidade actual em stock.")
    limite_minimo: int = Field(..., ge=0, description="Quantidade mínima desejada.")
    alerta: bool = Field(
        ...,
        description="True quando quantidade <= limite_minimo. Calculado pelo service.",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "peca_id": 1,
                "peca_referencia": "PEC-BAT-001",
                "peca_nome": "Bateria 36V 7.5Ah Xiaomi",
                "loja_id": 1,
                "loja_nome": "DLMCare Lisboa",
                "quantidade": 3,
                "limite_minimo": 5,
                "alerta": True,
            }
        },
    )


# ── Schema de entrada de stock ────────────────────────────────────────────────


class StockEntradaRequest(BaseModel):
    """Body do POST /api/v1/stock/entradas."""

    loja_id: int = Field(..., gt=0, description="Loja que recebe o stock.")
    peca_id: int = Field(..., gt=0, description="Peça a dar entrada.")
    quantidade: int = Field(..., gt=0, description="Quantidade a adicionar. Deve ser > 0.")
    observacoes: str | None = Field(None, description="Observações (ex: referência da fatura do fornecedor).")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "loja_id": 1,
                "peca_id": 1,
                "quantidade": 10,
                "observacoes": "Reposição mensal. Fatura fornecedor #F2026-042.",
            }
        }
    )


class StockEntradaResponse(BaseModel):
    """Resposta ao registo de uma entrada de stock."""

    peca_id: int
    peca_nome: str
    loja_id: int
    quantidade_anterior: int = Field(..., ge=0)
    quantidade_adicionada: int = Field(..., gt=0)
    quantidade_atual: int = Field(..., ge=0)
    alerta: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "peca_id": 1,
                "peca_nome": "Bateria 36V 7.5Ah Xiaomi",
                "loja_id": 1,
                "quantidade_anterior": 3,
                "quantidade_adicionada": 10,
                "quantidade_atual": 13,
                "alerta": False,
            }
        },
    )


# ── Schema de transferência de stock ─────────────────────────────────────────


class StockTransferenciaRequest(BaseModel):
    """Body do POST /api/v1/stock/transferencias."""

    peca_id: int = Field(..., gt=0, description="Peça a transferir.")
    loja_origem_id: int = Field(..., gt=0, description="Loja de origem.")
    loja_destino_id: int = Field(..., gt=0, description="Loja de destino.")
    quantidade: int = Field(..., gt=0, description="Quantidade a transferir. Deve ser > 0.")
    observacoes: str | None = Field(None, description="Observações opcionais.")

    @model_validator(mode="after")
    def lojas_distintas(self) -> StockTransferenciaRequest:
        if self.loja_origem_id == self.loja_destino_id:
            raise ValueError(
                "A loja de origem e a loja de destino não podem ser a mesma."
            )
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "peca_id": 1,
                "loja_origem_id": 1,
                "loja_destino_id": 2,
                "quantidade": 2,
                "observacoes": "Cedência urgente para Porto.",
            }
        }
    )


class StockTransferenciaResponse(BaseModel):
    """Resposta ao registo de uma transferência de stock."""

    peca_id: int
    peca_nome: str
    loja_origem_id: int
    loja_destino_id: int
    quantidade_transferida: int = Field(..., gt=0)
    stock_origem_apos: int = Field(..., ge=0)
    stock_destino_apos: int = Field(..., ge=0)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "peca_id": 1,
                "peca_nome": "Bateria 36V 7.5Ah Xiaomi",
                "loja_origem_id": 1,
                "loja_destino_id": 2,
                "quantidade_transferida": 2,
                "stock_origem_apos": 11,
                "stock_destino_apos": 3,
            }
        },
    )
