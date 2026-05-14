from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.common import validate_nif, validate_telemovel


# ── Schema de atualização ────────────────────────────────────────────────────


class ClienteUpdate(BaseModel):
    """Body do PATCH /api/v1/clientes/{id}. Todos os campos são opcionais."""

    nome: str | None = Field(None, min_length=1)
    telemovel: str | None = None
    email: EmailStr | None = None
    morada: str | None = None

    @field_validator("telemovel")
    @classmethod
    def telemovel_valido(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return validate_telemovel(v)


# ── Schema de criação ─────────────────────────────────────────────────────────


class ClienteCreate(BaseModel):
    """Body do POST /api/v1/clientes."""

    nome: str = Field(..., min_length=1, description="Nome completo do cliente.")
    nif: str = Field(..., description="NIF português com 9 dígitos.")
    telemovel: str = Field(
        ..., description="Telemóvel português com 9 dígitos, começado por 9."
    )
    email: EmailStr | None = Field(None, description="Email de contacto (opcional).")
    morada: str | None = Field(None, description="Morada completa (opcional).")
    consentimento_rgpd: bool = Field(
        ..., description="Consentimento RGPD. Obrigatório ser true para registar."
    )

    @field_validator("nif")
    @classmethod
    def nif_valido(cls, v: str) -> str:
        return validate_nif(v)

    @field_validator("telemovel")
    @classmethod
    def telemovel_valido(cls, v: str) -> str:
        return validate_telemovel(v)

    @field_validator("consentimento_rgpd")
    @classmethod
    def rgpd_obrigatorio(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "O consentimento RGPD é obrigatório para registar um cliente."
            )
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "João Silva",
                "nif": "123456789",
                "telemovel": "912345678",
                "email": "joao.silva@email.com",
                "morada": "Rua das Flores 10, Lisboa",
                "consentimento_rgpd": True,
            }
        }
    )


# ── Schema de resposta ────────────────────────────────────────────────────────


class ClienteResponse(BaseModel):
    """Resposta standard de um cliente (listagens e criação)."""

    id: int
    nome: str
    nif: str
    telemovel: str
    email: str | None
    morada: str | None
    consentimento_rgpd: bool
    data_registo: datetime
    loja_id: int
    nivel_fidelizacao: int = Field(0, ge=0, le=5, description="Nível de fidelização (0–5) calculado do histórico de OS.")
    desconto_sugerido_pct: float = Field(0.0, ge=0.0, le=10.0, description="Desconto sugerido em % (nivel * 2, max 10%).")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nome": "João Silva",
                "nif": "123456789",
                "telemovel": "912345678",
                "email": "joao.silva@email.com",
                "morada": "Rua das Flores 10, Lisboa",
                "consentimento_rgpd": True,
                "data_registo": "2026-04-01T10:00:00Z",
                "loja_id": 1,
            }
        },
    )


# ── Schema de detalhe (com trotinetes) ────────────────────────────────────────


class TrotineteResumoEmCliente(BaseModel):
    """Resumo de trotinete embutido no detalhe do cliente."""

    id: int
    marca: str
    modelo: str
    numero_serie: str

    model_config = ConfigDict(from_attributes=True)


class ClienteDetalheResponse(ClienteResponse):
    """Resposta do GET /api/v1/clientes/{id} — inclui trotinetes associadas."""

    trotinetes: list[TrotineteResumoEmCliente] = Field(
        default_factory=list,
        description="Trotinetes registadas em nome deste cliente.",
    )


# ── Resumo para respostas aninhadas ───────────────────────────────────────────


class ClienteResumo(BaseModel):
    """Versão mínima usada em respostas de OS e faturas."""

    id: int
    nome: str
    nif: str
    telemovel: str

    model_config = ConfigDict(from_attributes=True)


# ── Histórico de ordens do cliente ────────────────────────────────────────────


class ClienteHistoricoItem(BaseModel):
    """Item do histórico de serviços de um cliente."""

    id: int = Field(..., description="ID da ordem de serviço.")
    trotinete_numero_serie: str
    descricao: str
    estado: str
    data_entrada: datetime
    data_conclusao: datetime | None
    valor_final: float | None = Field(
        None, description="Valor final faturado. Null se ainda não faturado."
    )

    model_config = ConfigDict(from_attributes=True)
