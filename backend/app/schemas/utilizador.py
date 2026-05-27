from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Enum: perfis de utilizador ────────────────────────────────────────────────


class PerfilUtilizador(str, Enum):
    ADMINISTRADOR = "ADMINISTRADOR"
    GERENTE_LOJA = "GERENTE_LOJA"
    RECECIONISTA = "RECECIONISTA"
    MECANICO = "MECANICO"


# ── Schemas de utilizador ─────────────────────────────────────────────────────


class UtilizadorBase(BaseModel):
    nome: str = Field(..., min_length=1, description="Nome completo do utilizador.")
    email: EmailStr = Field(..., description="Email de login.")
    perfil: PerfilUtilizador = Field(..., description="Perfil de acesso.")
    loja_id: int | None = Field(
        None,
        description=(
            "ID da loja associada. Obrigatório para GERENTE_LOJA, RECECIONISTA e MECANICO. "
            "Null para ADMINISTRADOR."
        ),
    )
    ativo: bool = Field(True, description="Indica se a conta está activa.")
    comissao: int | None = Field(
        None,
        description="Percentagem de cada serviço. Apenas para o perfil MECANICO."
    )
    salario_base: float | None = Field(
        None,
        description="Salário base mensal em euros.",
    )


class UtilizadorCreate(UtilizadorBase):
    """Schema para a criação de um novo utilizador."""

    password: str = Field(..., min_length=6, description="Palavra-passe em texto simples.")


class UtilizadorResponse(UtilizadorBase):
    """Resposta completa de um utilizador. Não expõe password_hash."""

    id: int = Field(..., description="ID interno do utilizador.")
    loja_nome: str | None = Field(None, description="Nome da loja associada.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 2,
                "nome": "Ana Rececionista",
                "email": "ana.lisboa@dlmcare.pt",
                "perfil": "RECECIONISTA",
                "loja_id": 1,
                "loja_nome": "DLMCare Lisboa",
                "ativo": True,
            }
        },
    )


class UtilizadorUpdate(BaseModel):
    """Schema para actualizar um utilizador existente (campos opcionais)."""

    nome: str | None = Field(None, min_length=1)
    email: EmailStr | None = None
    perfil: PerfilUtilizador | None = None
    loja_id: int | None = None
    ativo: bool | None = None
    comissao: int | None = None
    salario_base: float | None = None


class PasswordResetRequest(BaseModel):
    """Body do PATCH /utilizadores/{id}/password — apenas ADMINISTRADOR."""

    nova_password: str = Field(..., min_length=6, description="Nova palavra-passe em texto simples.")


class UtilizadorResumo(BaseModel):
    """Versão resumida usada em respostas aninhadas (ex: mecanico em OS)."""

    id: int
    nome: str
    perfil: PerfilUtilizador

    model_config = ConfigDict(from_attributes=True)
