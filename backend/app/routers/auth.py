from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db

from app.auth.dependencies import get_current_user
from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["autenticação"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=201,
    summary="Autenticar utilizador",
    responses={
        401: {"description": "Credenciais inválidas"},
        403: {"description": "Conta inativa"},
    },
)
def login(body: LoginRequest, request: Request, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    ip = request.client.host if request.client else None
    return service.login(body.email, body.password, ip=ip)


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Renovar tokens",
    responses={
        401: {"description": "Refresh token inválido ou expirado"},
    },
)
def refresh(body: RefreshTokenRequest, service: AuthService = Depends(get_auth_service)) -> RefreshTokenResponse:
    return service.refresh(body.refresh_token)


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Dados do utilizador autenticado",
    responses={
        401: {"description": "Token inválido ou expirado"},
    },
)
def me(current_user: CurrentUserResponse = Depends(get_current_user)) -> CurrentUserResponse:
    return current_user
