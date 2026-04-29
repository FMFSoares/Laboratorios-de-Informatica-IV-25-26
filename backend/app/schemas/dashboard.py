from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


# ── Sub-schemas do dashboard ──────────────────────────────────────────────────


class DashboardPeriodo(BaseModel):
    """Intervalo de datas do relatório."""

    inicio: date
    fim: date

    model_config = ConfigDict(from_attributes=True)


class OrdensConcluidasPorLoja(BaseModel):
    """Ordens concluídas agrupadas por loja."""

    loja_id: int
    loja_nome: str
    total: int = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)


class PecaAbaixoStockMinimo(BaseModel):
    """Peça cujo stock está abaixo do limite mínimo configurado."""

    peca_id: int
    peca_nome: str
    loja_id: int
    loja_nome: str
    quantidade: int = Field(..., ge=0)
    limite_minimo: int = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)


class EficienciaMecanico(BaseModel):
    """Métricas de eficiência por mecânico."""

    mecanico_id: int
    nome: str
    ordens_concluidas: int = Field(..., ge=0)
    tempo_medio_minutos: int | None = Field(
        None,
        ge=0,
        description="Tempo médio de reparação em minutos (métricas internas).",
    )

    model_config = ConfigDict(from_attributes=True)


# ── Response principal do dashboard ──────────────────────────────────────────


class DashboardResponse(BaseModel):
    """
    Resposta do GET /api/v1/dashboard.
    Todos os valores numéricos são >= 0.
    Na Etapa 3, retornado pelo service com dados mockados.
    """

    periodo: DashboardPeriodo
    ordens_por_estado: dict[str, int] = Field(
        ...,
        description=(
            "Contagem de ordens por estado. "
            "Chaves correspondem aos valores de EstadoOrdemServico."
        ),
    )
    ordens_concluidas_por_loja: list[OrdensConcluidasPorLoja] = Field(
        default_factory=list
    )
    tempo_medio_reparacao_minutos: int | None = Field(
        None, ge=0, description="Tempo médio de reparação em toda a rede (ou loja)."
    )
    faturacao_total: float = Field(
        ..., ge=0.0, description="Total faturado no período."
    )
    pecas_abaixo_stock_minimo: list[PecaAbaixoStockMinimo] = Field(
        default_factory=list,
        description="Peças com stock abaixo do limite mínimo em alguma loja.",
    )
    eficiencia_por_mecanico: list[EficienciaMecanico] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "periodo": {"inicio": "2026-04-01", "fim": "2026-04-28"},
                "ordens_por_estado": {
                    "PENDENTE": 4,
                    "EM_DIAGNOSTICO": 2,
                    "AGUARDA_APROVACAO": 1,
                    "EM_REPARACAO": 5,
                    "AGUARDA_PECAS": 1,
                    "CONCLUIDA": 8,
                    "FATURADA": 22,
                    "CANCELADA": 3,
                },
                "ordens_concluidas_por_loja": [
                    {"loja_id": 1, "loja_nome": "DLMCare Lisboa", "total": 14},
                    {"loja_id": 2, "loja_nome": "DLMCare Porto", "total": 8},
                ],
                "tempo_medio_reparacao_minutos": 127,
                "faturacao_total": 3842.50,
                "pecas_abaixo_stock_minimo": [
                    {
                        "peca_id": 1,
                        "peca_nome": "Bateria 36V 7.5Ah Xiaomi",
                        "loja_id": 1,
                        "loja_nome": "DLMCare Lisboa",
                        "quantidade": 3,
                        "limite_minimo": 5,
                    }
                ],
                "eficiencia_por_mecanico": [
                    {
                        "mecanico_id": 3,
                        "nome": "Bruno Mecânico",
                        "ordens_concluidas": 12,
                        "tempo_medio_minutos": 118,
                    }
                ],
            }
        },
    )
