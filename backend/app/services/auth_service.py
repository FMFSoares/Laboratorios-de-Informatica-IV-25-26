from __future__ import annotations

from fastapi import HTTPException, status

from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.auth.password import hash_password, verify_password
from app.config import settings
from app.schemas.auth import (
    AuthUserInfo,
    CurrentUserResponse,
    LoginRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TokenResponse,
)
from app.schemas.utilizador import PerfilUtilizador

# ── Mock store ────────────────────────────────────────────────────────────────
# Substituir por repository real quando a BD estiver disponível.

_MOCK_USERS: list[dict] = [
    {
        "id": 1,
        "nome": "Admin DLMCare",
        "email": "admin@dlmcare.pt",
        "password_hash": hash_password("admin123"),
        "perfil": PerfilUtilizador.ADMINISTRADOR,
        "loja_id": None,
        "loja_nome": None,
        "ativo": True,
    },
    {
        "id": 2,
        "nome": "Carlos Gerente",
        "email": "carlos.porto@dlmcare.pt",
        "password_hash": hash_password("gerente123"),
        "perfil": PerfilUtilizador.GERENTE_LOJA,
        "loja_id": 1,
        "loja_nome": "DLMCare Porto",
        "ativo": True,
    },
    {
        "id": 3,
        "nome": "Ana Rececionista",
        "email": "ana.lisboa@dlmcare.pt",
        "password_hash": hash_password("password123"),
        "perfil": PerfilUtilizador.RECECIONISTA,
        "loja_id": 2,
        "loja_nome": "DLMCare Lisboa",
        "ativo": True,
    },
    {
        "id": 4,
        "nome": "João Mecânico",
        "email": "joao.braga@dlmcare.pt",
        "password_hash": hash_password("mecanico123"),
        "perfil": PerfilUtilizador.MECANICO,
        "loja_id": 3,
        "loja_nome": "DLMCare Braga",
        "ativo": True,
    },
]

_users_by_email: dict[str, dict] = {u["email"]: u for u in _MOCK_USERS}
_users_by_id: dict[int, dict] = {u["id"]: u for u in _MOCK_USERS}


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_token_payload(user: dict) -> dict:
    return {
        "sub": str(user["id"]),
        "nome": user["nome"],
        "email": user["email"],
        "perfil": user["perfil"].value,
        "loja_id": user["loja_id"],
        "loja_nome": user["loja_nome"],
    }


def _token_response(user: dict) -> TokenResponse:
    payload = _build_token_payload(user)
    return TokenResponse(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=AuthUserInfo(
            id=user["id"],
            nome=user["nome"],
            email=user["email"],
            perfil=user["perfil"],
            loja_id=user["loja_id"],
            loja_nome=user["loja_nome"],
        ),
    )


# ── Service functions ─────────────────────────────────────────────────────────


def login(credentials: LoginRequest) -> TokenResponse:
    user = _users_by_email.get(credentials.email)

    if user is None or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou password incorretos.",
            headers={"WWW-Authenticate": "Bearer", "X-Error-Code": "INVALID_CREDENTIALS"},
        )

    if not user["ativo"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta inativa. Contacte o administrador.",
            headers={"X-Error-Code": "ACCOUNT_INACTIVE"},
        )

    return _token_response(user)


def refresh(request: RefreshTokenRequest) -> RefreshTokenResponse:
    from jose import JWTError

    try:
        payload = decode_refresh_token(request.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer", "X-Error-Code": "TOKEN_INVALID"},
        )

    user_id = int(payload["sub"])
    user = _users_by_id.get(user_id)

    if user is None or not user["ativo"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilizador não encontrado ou inativo.",
            headers={"WWW-Authenticate": "Bearer", "X-Error-Code": "INVALID_CREDENTIALS"},
        )

    new_payload = _build_token_payload(user)
    return RefreshTokenResponse(
        access_token=create_access_token(new_payload),
        refresh_token=create_refresh_token(new_payload),
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def get_me(current_user: AuthUserInfo) -> CurrentUserResponse:
    user = _users_by_id.get(current_user.id)
    ativo = user["ativo"] if user else True

    return CurrentUserResponse(
        id=current_user.id,
        nome=current_user.nome,
        email=current_user.email,
        perfil=current_user.perfil,
        loja_id=current_user.loja_id,
        loja_nome=current_user.loja_nome,
        ativo=ativo,
    )
