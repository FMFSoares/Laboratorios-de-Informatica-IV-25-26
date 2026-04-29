from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Schemas de loja ───────────────────────────────────────────────────────────


class LojaBase(BaseModel):
    nome: str = Field(..., min_length=1, description="Nome da loja.")
    cidade: str = Field(..., min_length=1, description="Cidade onde a loja está localizada.")
    morada: str = Field(..., min_length=1, description="Morada completa.")
    telefone: str = Field(..., description="Número de telefone da loja.")
    email: EmailStr | None = Field(None, description="Email de contacto da loja.")


class LojaResponse(LojaBase):
    """Resposta completa de uma loja."""

    id: int = Field(..., description="ID interno da loja.")
    ativo: bool = Field(True, description="Indica se a loja está activa.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nome": "DLMCare Lisboa",
                "cidade": "Lisboa",
                "morada": "Av. da Liberdade 100, 1250-096 Lisboa",
                "telefone": "213000001",
                "email": "lisboa@dlmcare.pt",
                "ativo": True,
            }
        },
    )


class LojaResumo(BaseModel):
    """Versão resumida usada em respostas aninhadas."""

    id: int
    nome: str
    cidade: str

    model_config = ConfigDict(from_attributes=True)
