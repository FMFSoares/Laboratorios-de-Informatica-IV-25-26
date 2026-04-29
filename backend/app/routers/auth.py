from __future__ import annotations

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.schemas.auth import (
    AuthUserInfo,
    CurrentUserResponse,
    LoginRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TokenResponse,
)
from app.schemas.common import ErrorResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=201,
    responses={
        401: {"model": ErrorResponse, "description": "Credenciais inválidas."},
        403: {"model": ErrorResponse, "description": "Conta inativa."},
    },
    summary="Login",
    description="Autentica um utilizador com email e password. Devolve um par de tokens JWT.",
)
def login(credentials: LoginRequest) -> TokenResponse:
    return auth_service.login(credentials)


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=200,
    responses={
        401: {"model": ErrorResponse, "description": "Refresh token inválido ou expirado."},
    },
    summary="Renovar token",
    description="Troca um refresh token válido por um novo par de tokens JWT.",
)
def refresh(request: RefreshTokenRequest) -> RefreshTokenResponse:
    return auth_service.refresh(request)


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=200,
    responses={
        401: {"model": ErrorResponse, "description": "Token ausente ou inválido."},
    },
    summary="Utilizador atual",
    description="Devolve os dados do utilizador autenticado com base no access token.",
)
def me(current_user: AuthUserInfo = Depends(get_current_user)) -> CurrentUserResponse:
    return auth_service.get_me(current_user)
