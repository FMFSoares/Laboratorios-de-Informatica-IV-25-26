from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# ── Enums ─────────────────────────────────────────────────────────────────────


class EstadoOrdemServico(str, Enum):
    PENDENTE = "PENDENTE"
    EM_DIAGNOSTICO = "EM_DIAGNOSTICO"
    AGUARDA_APROVACAO = "AGUARDA_APROVACAO"
    EM_REPARACAO = "EM_REPARACAO"
    AGUARDA_PECAS = "AGUARDA_PECAS"
    CONCLUIDA = "CONCLUIDA"
    FATURADA = "FATURADA"
    CANCELADA = "CANCELADA"


class PrioridadeOrdemServico(str, Enum):
    BAIXA = "BAIXA"
    NORMAL = "NORMAL"
    ALTA = "ALTA"
    URGENTE = "URGENTE"


# ── Schemas de peças aplicadas numa OS ───────────────────────────────────────


class PecaAplicadaRequest(BaseModel):
    """Body do POST /api/v1/ordens-servico/{id}/pecas."""

    peca_id: int = Field(..., gt=0, description="ID da peça a aplicar.")
    quantidade: int = Field(..., gt=0, description="Quantidade utilizada. Deve ser > 0.")

    model_config = ConfigDict(
        json_schema_extra={"example": {"peca_id": 1, "quantidade": 1}}
    )


class PecaAplicadaResumo(BaseModel):
    """Peça aplicada embutida na resposta de detalhe da OS."""

    peca_id: int
    peca_nome: str
    quantidade: int = Field(..., gt=0)
    preco_venda_unitario: float = Field(
        ...,
        ge=0.0,
        description=(
            "Preço de venda no momento da aplicação. "
            "Registado para consistência histórica da fatura."
        ),
    )
    subtotal: float = Field(
        ..., ge=0.0, description="quantidade × preco_venda_unitario."
    )

    model_config = ConfigDict(from_attributes=True)


class PecaAplicadaResponse(PecaAplicadaResumo):
    """Resposta ao POST /api/v1/ordens-servico/{id}/pecas."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "peca_id": 1,
                "peca_nome": "Bateria 36V 7.5Ah Xiaomi",
                "quantidade": 1,
                "preco_venda_unitario": 89.90,
                "subtotal": 89.90,
            }
        },
    )


# ── Schemas de info aninhada (sem imports de outros módulos de schemas) ────────


class _OSClienteInfo(BaseModel):
    id: int
    nome: str
    telemovel: str

    model_config = ConfigDict(from_attributes=True)


class _OSTrotineteInfo(BaseModel):
    id: int
    marca: str
    modelo: str
    numero_serie: str

    model_config = ConfigDict(from_attributes=True)


class _OSMecanicoInfo(BaseModel):
    id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)


# ── Schema de criação ─────────────────────────────────────────────────────────


class OrdemServicoCreate(BaseModel):
    """Body do POST /api/v1/ordens-servico."""

    trotinete_id: int = Field(..., gt=0, description="Trotinete a reparar.")
    loja_id: int = Field(..., gt=0, description="Loja onde a ordem é criada.")
    mecanico_id: int | None = Field(
        None, gt=0, description="Mecânico responsável (pode ser atribuído depois)."
    )
    descricao_problema: str = Field(
        ..., min_length=1, description="Descrição do problema reportado pelo cliente."
    )
    prioridade: PrioridadeOrdemServico = Field(
        PrioridadeOrdemServico.NORMAL, description="Prioridade da ordem de serviço."
    )
    preco_servico: float = Field(
        0.0,
        ge=0.0,
        description=(
            "Preço do serviço. Calculado automaticamente pelo mecânico no diagnóstico. "
            "Pode ser enviado a 0 na criação da OS."
        ),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "trotinete_id": 3,
                "loja_id": 1,
                "mecanico_id": 3,
                "descricao_problema": "Não arranca. Bateria parece descarregada mesmo após carga.",
                "prioridade": "NORMAL",
            }
        }
    )


# ── Schema de resposta base ───────────────────────────────────────────────────


class OrdemServicoResponse(BaseModel):
    """
    Resposta ao criar uma OS (POST) e em listagens.
    Usa IDs em vez de objectos aninhados.
    """

    id: int
    numero: str = Field(..., description="Número legível da OS (ex: OS-2026-0010).")
    trotinete_id: int
    cliente_id: int
    loja_id: int
    mecanico_id: int | None
    estado: EstadoOrdemServico
    prioridade: PrioridadeOrdemServico
    descricao_problema: str
    preco_servico: float = Field(
        ...,
        ge=0.0,
        description="Preço tabelado do serviço. Base do cálculo da fatura.",
    )
    data_entrada: datetime
    data_conclusao: datetime | None
    pecas_aplicadas: list[PecaAplicadaResumo] = Field(default_factory=list)
    tempo_total_minutos: int | None = Field(
        None,
        description=(
            "Tempo acumulado de trabalho (métricas internas). "
            "Não é usado para calcular o valor da fatura."
        ),
    )

    model_config = ConfigDict(from_attributes=True)


# ── Schema de resumo para listagens ──────────────────────────────────────────


class OrdemServicoResumo(BaseModel):
    """Versão resumida para listagens paginadas."""

    id: int
    numero: str
    estado: EstadoOrdemServico
    prioridade: PrioridadeOrdemServico
    loja_id: int
    loja_nome: str | None
    cliente_nome: str | None
    trotinete_numero_serie: str | None
    mecanico_id: int | None = None
    mecanico_nome: str | None
    data_entrada: datetime
    data_conclusao: datetime | None = None
    em_atraso: bool = Field(False, description="True se o tempo decorrido supera a média das OS concluídas.")
    minutos_em_atraso: int | None = Field(None, description="Minutos acima da média, quando em atraso.")
    tem_timer_ativo: bool = Field(False, description="True se o mecânico tem um registo de tempo em curso nesta OS.")

    model_config = ConfigDict(from_attributes=True)


# ── Schemas de observações internas ──────────────────────────────────────────


class OrdemServicoObservacaoCreate(BaseModel):
    """Body do POST /api/v1/ordens-servico/{id}/observacoes."""

    texto: str = Field(..., min_length=1, max_length=1000, description="Texto da observação interna.")

    model_config = ConfigDict(
        json_schema_extra={"example": {"texto": "Necessita peça do fabricante Xiaomi — encomendar antes de avançar."}}
    )


class OrdemServicoObservacaoResponse(BaseModel):
    """Observação interna devolvida na lista e na resposta de criação."""

    id: int
    texto: str
    autor_id: int
    autor_nome: str
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Schemas de diagnóstico ───────────────────────────────────────────────────


class OSServicoResumo(BaseModel):
    id: int
    servico_id: int | None
    nome: str
    preco: float

    model_config = ConfigDict(from_attributes=True)


class DiagnosticoItemCreate(BaseModel):
    servico_id: int | None = Field(None, description="ID do serviço do catálogo. Null se personalizado.")
    nome: str = Field(..., min_length=1, max_length=200, description="Nome do serviço/problema diagnosticado.")
    preco: float = Field(..., ge=0.0, description="Preço acordado para este item.")


class DiagnosticoSubmit(BaseModel):
    itens: list[DiagnosticoItemCreate] = Field(..., min_length=1, description="Lista de serviços/problemas diagnosticados.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "itens": [
                    {"servico_id": 1, "nome": "Revisão geral", "preco": 35.00},
                    {"servico_id": None, "nome": "Substituição de rolamento dianteiro", "preco": 18.50},
                ]
            }
        }
    )


# ── Schema de detalhe (com objectos aninhados) ────────────────────────────────


class OrdemServicoDetalheResponse(BaseModel):
    """
    Resposta completa do GET /api/v1/ordens-servico/{id}.
    Inclui cliente, trotinete e mecânico como objectos aninhados.
    """

    id: int
    numero: str
    estado: EstadoOrdemServico
    prioridade: PrioridadeOrdemServico
    loja_id: int
    loja_nome: str | None
    cliente: _OSClienteInfo
    trotinete: _OSTrotineteInfo
    mecanico: _OSMecanicoInfo | None
    descricao_problema: str
    preco_servico: float = Field(
        ...,
        ge=0.0,
        description="Preço tabelado do serviço. Base do cálculo da fatura.",
    )
    servicos_diagnostico: list[OSServicoResumo] = Field(default_factory=list)
    pecas_aplicadas: list[PecaAplicadaResumo] = Field(default_factory=list)
    subtotal_pecas: float = Field(
        0.0,
        ge=0.0,
        description="Soma de (quantidade × preco_venda_unitario) de todas as peças aplicadas.",
    )
    valor_estimado_total: float = Field(
        0.0,
        ge=0.0,
        description=(
            "Estimativa: preco_servico + subtotal_pecas. "
            "Valor final confirmado apenas na fatura."
        ),
    )
    tempo_total_minutos: int | None = Field(
        None,
        description=(
            "Tempo acumulado (métricas internas). "
            "Não é base de cálculo da fatura."
        ),
    )
    data_entrada: datetime
    data_conclusao: datetime | None
    fatura_id: int | None = Field(None, description="ID da fatura, quando emitida.")
    em_atraso: bool = Field(False, description="True se o tempo decorrido supera a média das OS concluídas.")
    minutos_em_atraso: int | None = Field(None, description="Minutos acima da média, quando em atraso.")
    inicio_tempo_atual: datetime | None = Field(None, description="Timestamp de início da sessão de tempo activa, ou null se não há timer a correr.")
    observacoes: list[OrdemServicoObservacaoResponse] = Field(default_factory=list)
    estado_anterior: EstadoOrdemServico | None = Field(None, description="Estado imediatamente anterior (preenchido apenas em respostas a PATCH /estado).")

    model_config = ConfigDict(from_attributes=True)


# ── Schema de transição de estado ────────────────────────────────────────────


class OrdemServicoEstadoUpdate(BaseModel):
    """Body do PATCH /api/v1/ordens-servico/{id}/estado."""

    novo_estado: EstadoOrdemServico = Field(
        ...,
        description=(
            "Novo estado pretendido. "
            "As transições válidas são validadas pelo service, não aqui."
        ),
    )
    observacao: str | None = Field(
        None, description="Justificação ou nota associada à transição."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "novo_estado": "EM_REPARACAO",
                "observacao": "Cliente aprovou orçamento por telefone.",
            }
        }
    )


class OrdemServicoEstadoUpdateResponse(BaseModel):
    """Resposta ao PATCH de estado."""

    id: int
    estado_anterior: EstadoOrdemServico
    estado_atual: EstadoOrdemServico
    alterado_por: str = Field(..., description="Nome do utilizador que fez a alteração.")
    data_alteracao: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Schemas de registo de tempos (métricas internas) ─────────────────────────


class TempoInicioResponse(BaseModel):
    """
    Resposta ao POST /api/v1/ordens-servico/{id}/tempos/iniciar.
    O tempo registado serve apenas para métricas internas.
    Não é usado no cálculo do valor da fatura.
    """

    ordem_servico_id: int
    inicio: datetime

    model_config = ConfigDict(from_attributes=True)


class TempoParagemResponse(BaseModel):
    """
    Resposta ao POST /api/v1/ordens-servico/{id}/tempos/parar.
    Acumula minutos para métricas. Não afecta o valor da fatura.
    """

    ordem_servico_id: int
    inicio: datetime
    fim: datetime
    minutos_esta_sessao: int = Field(..., ge=0)
    tempo_total_acumulado_minutos: int = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)


# ── Schema de reatribuição de mecânico ───────────────────────────────────────


class OrdemServicoMecanicoUpdate(BaseModel):
    """Body do PATCH /api/v1/ordens-servico/{id}/mecanico."""

    mecanico_id: int | None = Field(
        ...,
        description="ID do novo mecânico. Enviar null para desatribuir.",
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"mecanico_id": 4}}
    )


class OrdemServicoMecanicoUpdateResponse(BaseModel):
    """Resposta ao PATCH de mecânico."""

    id: int
    mecanico_id: int | None
    mecanico_nome: str | None

    model_config = ConfigDict(from_attributes=True)
