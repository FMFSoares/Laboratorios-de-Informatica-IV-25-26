from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Schema de criação ─────────────────────────────────────────────────────────


class TrotineteCreate(BaseModel):
    """Body do POST /api/v1/trotinetes."""

    cliente_id: int = Field(..., gt=0, description="ID do cliente proprietário.")
    marca: str = Field(..., min_length=1, description="Marca da trotinete.")
    modelo: str = Field(..., min_length=1, description="Modelo da trotinete.")
    numero_serie: str = Field(
        ..., min_length=1, description="Número de série único da trotinete."
    )
    ano_compra: int | None = Field(
        None, description="Ano de compra original (2000–2100)."
    )
    cor: str | None = Field(None, description="Cor da trotinete (opcional).")
    observacoes_tecnicas: str | None = Field(
        None, description="Notas técnicas relevantes (opcional)."
    )

    @field_validator("ano_compra")
    @classmethod
    def ano_plausivel(cls, v: int | None) -> int | None:
        if v is not None and not (2000 <= v <= 2100):
            raise ValueError("O ano de compra deve estar entre 2000 e 2100.")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cliente_id": 1,
                "marca": "Xiaomi",
                "modelo": "Mi Electric Scooter 3",
                "numero_serie": "XM2024ABC123",
                "ano_compra": 2024,
                "cor": "Preto",
                "observacoes_tecnicas": "Bateria substituída em 2025. Controlador original.",
            }
        }
    )


# ── Schema de resposta ────────────────────────────────────────────────────────


class TrotineteResponse(BaseModel):
    """Resposta standard de uma trotinete (criação e listagens)."""

    id: int
    cliente_id: int
    marca: str
    modelo: str
    numero_serie: str
    ano_compra: int | None
    cor: str | None
    observacoes_tecnicas: str | None
    data_registo: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 3,
                "cliente_id": 1,
                "marca": "Xiaomi",
                "modelo": "Mi Electric Scooter 3",
                "numero_serie": "XM2024ABC123",
                "ano_compra": 2024,
                "cor": "Preto",
                "observacoes_tecnicas": "Bateria substituída em 2025. Controlador original.",
                "data_registo": "2026-04-28T14:00:00Z",
            }
        },
    )


# ── Schema de detalhe (com info do cliente e contagem de ordens) ──────────────


class ClienteResumoEmTrotinete(BaseModel):
    """Resumo do cliente embutido no detalhe da trotinete."""

    id: int
    nome: str
    telemovel: str

    model_config = ConfigDict(from_attributes=True)


class TrotineteDetalheResponse(TrotineteResponse):
    """Resposta do GET /api/v1/trotinetes/{id} — inclui cliente e contagem de ordens."""

    cliente: ClienteResumoEmTrotinete
    total_ordens: int = Field(
        0, ge=0, description="Total de ordens de serviço associadas a esta trotinete."
    )


# ── Resumo para respostas aninhadas ───────────────────────────────────────────


class TrotineteResumo(BaseModel):
    """Versão mínima usada em respostas de OS e faturas."""

    id: int
    marca: str
    modelo: str
    numero_serie: str

    model_config = ConfigDict(from_attributes=True)
