from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

DataT = TypeVar("DataT")


# ── Validators reutilizáveis (chamados via @field_validator nos schemas) ───────


def validate_nif(value: str) -> str:
    """NIF português: validação exata com dígito de controlo (Modulus 11)."""
    if not isinstance(value, str) or not value.isdigit() or len(value) != 9:
        raise ValueError("NIF deve ter exatamente 9 dígitos numéricos.")

    total = sum(int(value[i]) * (9 - i) for i in range(8))
    resto = total % 11
    check_digit = 0 if resto < 2 else 11 - resto

    if check_digit != int(value[8]):
        raise ValueError("NIF inválido (falha no dígito de controlo).")

    return value


def validate_telemovel(value: str) -> str:
    """Telemóvel português: 9 dígitos, começa por 9."""
    if not isinstance(value, str) or not value.isdigit() or len(value) != 9:
        raise ValueError("Telemóvel deve ter exatamente 9 dígitos numéricos.")
    if not value.startswith("9"):
        raise ValueError("Telemóvel português deve começar por 9.")
    return value


# ── ConfigDict base para schemas de resposta (futura integração com ORM) ──────

response_config = ConfigDict(from_attributes=True)


# ── Resposta de erro padrão ────────────────────────────────────────────────────


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Mensagem de erro legível para o utilizador.")
    code: str | None = Field(None, description="Código de erro interno da API.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Recurso não encontrado.",
                "code": "RESOURCE_NOT_FOUND",
            }
        }
    )


# ── Resposta genérica com dados e mensagem ─────────────────────────────────────


class DataResponse(BaseModel, Generic[DataT]):
    """Resposta padrão de sucesso para operações que devolvem um único recurso."""

    data: DataT
    message: str | None = Field(None, description="Mensagem de confirmação opcional.")

    model_config = ConfigDict(from_attributes=True)


# ── Resposta paginada genérica ─────────────────────────────────────────────────


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Resposta padrão de sucesso para listagens paginadas."""

    data: list[DataT]
    total: int = Field(..., ge=0, description="Total de registos encontrados.")
    page: int = Field(..., ge=1, description="Página atual.")
    page_size: int = Field(..., ge=1, description="Tamanho da página.")
    pages: int = Field(..., ge=0, description="Total de páginas disponíveis.")

    model_config = ConfigDict(from_attributes=True)


# ── Parâmetros de paginação (query params) ─────────────────────────────────────


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Página a devolver (base 1).")
    page_size: int = Field(
        20,
        ge=1,
        le=100,
        description="Resultados por página. Mínimo: 1, máximo: 100.",
    )
