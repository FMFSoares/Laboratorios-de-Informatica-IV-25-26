from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.utilizador import PerfilUtilizador


# ── Request: login ────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email de login do utilizador.")
    password: str = Field(..., min_length=1, description="Password em texto simples.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "ana.lisboa@dlmcare.pt",
                "password": "password123",
            }
        }
    )


# ── Info do utilizador embutida no token de login ─────────────────────────────


class AuthUserInfo(BaseModel):
    """Dados do utilizador incluídos na resposta do login."""

    id: int
    nome: str
    email: str
    perfil: PerfilUtilizador
    loja_id: int | None
    loja_nome: str | None

    model_config = ConfigDict(from_attributes=True)


# ── Response: login ───────────────────────────────────────────────────────────


class TokenResponse(BaseModel):
    """Resposta ao login bem-sucedido."""

    access_token: str = Field(..., description="JWT de acesso (curta duração).")
    refresh_token: str = Field(..., description="JWT de renovação (longa duração).")
    token_type: str = Field("bearer", description="Tipo de token. Sempre 'bearer'.")
    expires_in: int = Field(
        ..., description="Segundos até o access_token expirar."
    )
    user: AuthUserInfo = Field(..., description="Dados do utilizador autenticado.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 28800,
                "user": {
                    "id": 2,
                    "nome": "Ana Rececionista",
                    "email": "ana.lisboa@dlmcare.pt",
                    "perfil": "RECECIONISTA",
                    "loja_id": 1,
                    "loja_nome": "DLMCare Lisboa",
                },
            }
        }
    )


# ── Request: refresh token ────────────────────────────────────────────────────


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT de renovação emitido no login.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


# ── Response: refresh token ───────────────────────────────────────────────────


class RefreshTokenResponse(BaseModel):
    """Resposta à renovação de token."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Segundos até o novo access_token expirar.")


# ── Response: utilizador autenticado (/auth/me) ───────────────────────────────


class CurrentUserResponse(BaseModel):
    """Resposta do endpoint GET /auth/me."""

    id: int
    nome: str
    email: str
    perfil: PerfilUtilizador
    loja_id: int | None
    loja_nome: str | None
    ativo: bool

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
