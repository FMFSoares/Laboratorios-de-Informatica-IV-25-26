from __future__ import annotations

# [pendente de integração com BD]
# Utilizadores em memória para a Etapa 3.
# Quando os repositories reais estiverem disponíveis, substituir _get_user_by_email
# por uma query à BD sem alterar o router nem os schemas.

from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.config import settings
from app.schemas.auth import (
    AuthUserInfo,
    RefreshTokenResponse,
    TokenResponse,
)
from app.schemas.utilizador import PerfilUtilizador

# ── Utilizadores mockados ─────────────────────────────────────────────────────
# Hashes gerados com bcrypt 5.x (cost factor 12).

_MOCK_USERS: list[dict] = [
    {
        "id": 1,
        "nome": "Admin DLMCare",
        "email": "admin@dlmcare.pt",
        "password_hash": "$2b$12$Ljzvo8.JjstrAfsohpMqauw4OdBbLNksDIvP5eKKHaBEWRS5c4t4K",
        "perfil": PerfilUtilizador.ADMINISTRADOR,
        "loja_id": None,
        "loja_nome": None,
        "ativo": True,
    },
    {
        "id": 2,
        "nome": "Gerente Porto",
        "email": "gerente.porto@dlmcare.pt",
        "password_hash": "$2b$12$d1NsqHAUS7myTvUEz3pef.Xfvpa5Du7.43v9zjIJVJek8t97LWC0G",
        "perfil": PerfilUtilizador.GERENTE_LOJA,
        "loja_id": 1,
        "loja_nome": "DLMCare Porto",
        "ativo": True,
    },
    {
        "id": 3,
        "nome": "Ana Rececionista",
        "email": "ana.lisboa@dlmcare.pt",
        "password_hash": "$2b$12$fI2Bd1BsD7iZYQvzuKojZu2R/9A5IsqjyqQajWj4Zv1H7wuY/Rkwa",
        "perfil": PerfilUtilizador.RECECIONISTA,
        "loja_id": 1,
        "loja_nome": "DLMCare Porto",
        "ativo": True,
    },
    {
        "id": 4,
        "nome": "João Mecânico",
        "email": "joao.mecanico@dlmcare.pt",
        "password_hash": "$2b$12$97e79p34JpiM2uZbSjJbvu3j6Q3HJtD1FSA67mNC8HmoVT5PKQOru",
        "perfil": PerfilUtilizador.MECANICO,
        "loja_id": 1,
        "loja_nome": "DLMCare Porto",
        "ativo": True,
    },
]


def _get_user_by_email(email: str) -> dict | None:
    email_lower = email.lower()
    return next((u for u in _MOCK_USERS if u["email"].lower() == email_lower), None)


def _user_to_payload(user: dict) -> dict:
    return {
        "sub": str(user["id"]),
        "nome": user["nome"],
        "email": user["email"],
        "perfil": user["perfil"].value,
        "loja_id": user["loja_id"],
        "loja_nome": user["loja_nome"],
        "ativo": user["ativo"],
    }


def _user_to_auth_info(user: dict) -> AuthUserInfo:
    return AuthUserInfo(
        id=user["id"],
        nome=user["nome"],
        email=user["email"],
        perfil=user["perfil"],
        loja_id=user["loja_id"],
        loja_nome=user["loja_nome"],
    )


# ── Casos de uso ──────────────────────────────────────────────────────────────


def login(email: str, password: str) -> TokenResponse:
    user = _get_user_by_email(email)

    if user is None or not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Credenciais inválidas.", "code": "INVALID_CREDENTIALS"},
        )

    if not user["ativo"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"detail": "Conta inativa.", "code": "ACCOUNT_INACTIVE"},
        )

    payload = _user_to_payload(user)
    return TokenResponse(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=_user_to_auth_info(user),
    )


def refresh(refresh_token: str) -> RefreshTokenResponse:
    payload = decode_token(refresh_token, expected_type="refresh")

    # Garante que o utilizador ainda existe e está ativo [pendente de integração com BD]
    user = _get_user_by_email(payload["email"])
    if user is None or not user["ativo"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Token inválido.", "code": "TOKEN_INVALID"},
        )

    new_payload = _user_to_payload(user)
    return RefreshTokenResponse(
        access_token=create_access_token(new_payload),
        refresh_token=create_refresh_token(new_payload),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
