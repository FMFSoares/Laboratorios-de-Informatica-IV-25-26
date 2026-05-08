from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ── Enum: tipos de evento de auditoria ───────────────────────────────────────


class TipoEventoAuditoria(str, Enum):
    LOGIN_SUCESSO = "LOGIN_SUCESSO"
    LOGIN_FALHA = "LOGIN_FALHA"
    ACESSO_NEGADO = "ACESSO_NEGADO"
    OS_ESTADO_ALTERADO = "OS_ESTADO_ALTERADO"
    STOCK_ENTRADA = "STOCK_ENTRADA"
    STOCK_TRANSFERENCIA = "STOCK_TRANSFERENCIA"
    FATURA_EMITIDA = "FATURA_EMITIDA"


# ── Schema de detalhe do evento (livre) ──────────────────────────────────────


class AuditoriaDetalhe(BaseModel):
    """
    Detalhe livre associado ao evento de auditoria.
    Estrutura depende do tipo de evento.
    Exemplos:
        OS_ESTADO_ALTERADO: {"ordem_servico_id": 10, "estado_anterior": "...", "estado_novo": "..."}
        STOCK_ENTRADA:       {"peca_id": 1, "loja_id": 1, "quantidade": 10}
        FATURA_EMITIDA:      {"fatura_id": 5, "ordem_servico_id": 10, "valor_final": 114.90}
    """

    dados: dict[str, Any] = Field(
        default_factory=dict,
        description="Dados estruturados do evento (varia por tipo).",
    )

    model_config = ConfigDict(from_attributes=True)


# ── Schema de item de auditoria ───────────────────────────────────────────────


class AuditoriaItemResponse(BaseModel):
    """Registo individual no log de auditoria."""

    id: int
    evento: TipoEventoAuditoria
    descricao: str = Field(..., description="Descrição legível do evento.")
    utilizador_id: int | None = Field(
        None, description="ID do utilizador que gerou o evento. Null para eventos de sistema."
    )
    
    utilizador_nome: str | None = Field(None, description="Nome do utilizador.")
    loja_id: int | None = Field(
        None, description="Loja associada ao evento. Null para eventos globais."
    )
    
    ip_origem: str | None = Field(None, description="IP do cliente que originou a acção.")
    timestamp: datetime = Field(..., description="Data e hora do evento (UTC).")
    detalhe: dict[str, Any] = Field(
        default_factory=dict,
        description="Dados adicionais do evento (estrutura varia por tipo).",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "evento": "OS_ESTADO_ALTERADO",
                "descricao": "OS #10 alterada de AGUARDA_APROVACAO para EM_REPARACAO",
                "utilizador_id": 2,
                "utilizador_nome": "Ana Rececionista",
                "loja_id": 1,
                "ip_origem": "192.168.1.10",
                "timestamp": "2026-04-28T11:00:00Z",
                "detalhe": {
                    "ordem_servico_id": 10,
                    "estado_anterior": "AGUARDA_APROVACAO",
                    "estado_novo": "EM_REPARACAO",
                },
            }
        },
    )
