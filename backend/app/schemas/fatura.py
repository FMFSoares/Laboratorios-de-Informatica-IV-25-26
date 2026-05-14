from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# ── Enum: estado da fatura ────────────────────────────────────────────────────


class EstadoFatura(str, Enum):
    EMITIDA = "EMITIDA"
    ANULADA = "ANULADA"


class DescontoTipo(str, Enum):
    PERCENTUAL = "PERCENTUAL"
    FIXO = "FIXO"


# ── Schemas de info aninhada na fatura ────────────────────────────────────────


class FaturaClienteInfo(BaseModel):
    """Dados do cliente impressos na fatura."""

    id: int
    nome: str
    nif: str
    morada: str | None
    email: str | None = None

    model_config = ConfigDict(from_attributes=True)


class FaturaTrotineteInfo(BaseModel):
    """Dados da trotinete impressos na fatura."""

    marca: str
    modelo: str
    numero_serie: str

    model_config = ConfigDict(from_attributes=True)


class FaturaServicoInfo(BaseModel):
    """
    Serviço prestado discriminado na fatura.
    preco_servico é o valor comercial/tabelado acordado na criação da OS.
    O tempo de mão de obra NÃO entra neste valor.
    """

    descricao: str
    preco_servico: float = Field(
        ...,
        ge=0.0,
        description=(
            "Preço tabelado do serviço. Definido na OS. "
            "Não calculado por tempo de mão de obra."
        ),
    )

    model_config = ConfigDict(from_attributes=True)


class FaturaPecaAplicada(BaseModel):
    """
    Linha de peça na fatura.
    subtotal = quantidade × preco_venda_unitario.
    preco_custo da peça é OMITIDO — é dado interno e nunca aparece em faturas.
    """

    peca_referencia: str
    peca_nome: str
    quantidade: int = Field(..., gt=0)
    preco_venda_unitario: float = Field(
        ...,
        ge=0.0,
        description=(
            "Preço de venda da peça no momento da aplicação (registado na OS). "
            "Nunca usar preco_custo no cálculo da fatura."
        ),
    )
    subtotal: float = Field(..., ge=0.0, description="quantidade × preco_venda_unitario.")

    model_config = ConfigDict(from_attributes=True)


class FaturaLojaInfo(BaseModel):
    """Dados da loja emitente impressos na fatura."""

    nome: str
    morada: str
    telefone: str

    model_config = ConfigDict(from_attributes=True)


# ── Request: criar fatura ─────────────────────────────────────────────────────


class FaturaEnviarEmailRequest(BaseModel):
    """Body do POST /api/v1/faturas/{id}/enviar-email."""

    email: str | None = Field(None, description="Email de destino. Se omitido, usa o email registado no cliente.")


class FaturaCreateRequest(BaseModel):
    """
    Body do POST /api/v1/faturas.

    Regras de negócio (validadas pelo service):
    - A OS deve estar em estado CONCLUIDA.
    - Não pode existir outra fatura para a mesma OS.
    - Ao emitir, o estado da OS transita automaticamente para FATURADA.
    """

    ordem_servico_id: int = Field(
        ..., gt=0, description="ID da ordem de serviço concluída a faturar."
    )
    desconto_tipo: DescontoTipo | None = Field(
        None, description="Tipo de desconto: PERCENTUAL (%) ou FIXO (€). Null se sem desconto."
    )
    desconto_valor: float = Field(
        0.0, ge=0.0, description="Valor do desconto (percentagem ou montante fixo)."
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"ordem_servico_id": 10, "desconto_tipo": "PERCENTUAL", "desconto_valor": 4.0}}
    )


# ── Response: fatura completa ─────────────────────────────────────────────────


class FaturaResponse(BaseModel):
    """
    Resposta completa da fatura.

    Regra de cálculo:
        valor_final = preco_servico + subtotal_pecas
        subtotal_pecas = Σ (quantidade × preco_venda_unitario)

    Campos ausentes propositadamente:
    - preco_custo das peças: dado interno, nunca exposto.
    - tempo de mão de obra: não entra diretamente no valor_final.
    """

    id: int
    numero: str = Field(..., description="Número da fatura (ex: FAT-2026-0005).")
    ordem_servico_id: int
    data_emissao: datetime
    estado: EstadoFatura
    cliente: FaturaClienteInfo
    trotinete: FaturaTrotineteInfo
    servico: FaturaServicoInfo
    pecas_aplicadas: list[FaturaPecaAplicada] = Field(default_factory=list)
    subtotal_pecas: float = Field(
        ...,
        ge=0.0,
        description="Σ (quantidade × preco_venda_unitario) de todas as peças aplicadas.",
    )
    desconto_tipo: DescontoTipo | None = Field(None, description="Tipo de desconto aplicado, ou null.")
    desconto_valor: float = Field(0.0, ge=0.0, description="Valor do desconto (% ou €).")
    valor_desconto: float = Field(0.0, ge=0.0, description="Montante descontado em €.")
    valor_final: float = Field(
        ...,
        ge=0.0,
        description="preco_servico + subtotal_pecas - valor_desconto. Calculado pelo service.",
    )
    loja: FaturaLojaInfo

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 5,
                "numero": "FAT-2026-0005",
                "ordem_servico_id": 10,
                "data_emissao": "2026-04-28T17:00:00Z",
                "estado": "EMITIDA",
                "cliente": {
                    "id": 1,
                    "nome": "João Silva",
                    "nif": "123456789",
                    "morada": "Rua das Flores 10, Lisboa",
                },
                "trotinete": {
                    "marca": "Xiaomi",
                    "modelo": "Mi Electric Scooter 3",
                    "numero_serie": "XM2024ABC123",
                },
                "servico": {
                    "descricao": "Diagnóstico + substituição de bateria",
                    "preco_servico": 25.00,
                },
                "pecas_aplicadas": [
                    {
                        "peca_referencia": "PEC-BAT-001",
                        "peca_nome": "Bateria 36V 7.5Ah Xiaomi",
                        "quantidade": 1,
                        "preco_venda_unitario": 89.90,
                        "subtotal": 89.90,
                    }
                ],
                "subtotal_pecas": 89.90,
                "valor_final": 114.90,
                "loja": {
                    "nome": "DLMCare Lisboa",
                    "morada": "Av. da Liberdade 100, 1250-096 Lisboa",
                    "telefone": "213000001",
                },
            }
        },
    )


# ── Resumo de fatura para listagens ──────────────────────────────────────────


class FaturaResumo(BaseModel):
    """Versão resumida para listagens paginadas de faturas."""

    id: int
    numero: str
    ordem_servico_id: int
    cliente_nome: str
    cliente_nif: str
    valor_final: float = Field(..., ge=0.0)
    data_emissao: datetime
    estado: EstadoFatura

    model_config = ConfigDict(from_attributes=True)
