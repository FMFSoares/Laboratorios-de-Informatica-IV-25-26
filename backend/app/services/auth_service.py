from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.utilizador_repository import UtilizadorRepository
from app.repositories.auditoria_repository import AuditoriaRepository
from app.schemas.auth import AuthUserInfo, RefreshTokenResponse, TokenResponse
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.auditoria import TipoEventoAuditoria
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.config import settings

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UtilizadorRepository(db)
        self.auditoria_repo = AuditoriaRepository(db)

    def _user_to_payload(self, u) -> dict:
        return {
            "sub": str(u.id),
            "nome": u.nome,
            "email": u.email,
            "perfil": u.perfil.value,
            "loja_id": u.loja_id,
            "loja_nome": u.loja.nome if u.loja else None,
            "ativo": u.ativo,
        }

    def _user_to_auth_info(self, u) -> AuthUserInfo:
        return AuthUserInfo(
            id=u.id,
            nome=u.nome,
            email=u.email,
            perfil=u.perfil,
            loja_id=u.loja_id,
            loja_nome=u.loja.nome if u.loja else None,
        )

    def login(self, email: str, password: str, ip: str | None = None) -> TokenResponse:
        user = self.repo.get_by_email(email)

        if user is None or not verify_password(password, user.password_hash):
            self.auditoria_repo.registar(
                evento=TipoEventoAuditoria.LOGIN_FALHA,
                descricao=f"Tentativa de login falhada para '{email}'",
                ip_origem=ip,
                detalhe={"email": email, "motivo": "credenciais_invalidas"},
            )
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"detail": "Credenciais inválidas.", "code": "INVALID_CREDENTIALS"},
            )

        if not user.ativo:
            self.auditoria_repo.registar(
                evento=TipoEventoAuditoria.LOGIN_FALHA,
                descricao=f"Tentativa de login — conta inativa: {user.nome}",
                ip_origem=ip,
                utilizador_id=user.id,
                loja_id=user.loja_id,
                detalhe={"email": email, "motivo": "conta_inativa"},
            )
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"detail": "Conta inativa.", "code": "ACCOUNT_INACTIVE"},
            )

        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.LOGIN_SUCESSO,
            descricao=f"Login bem-sucedido: {user.nome}",
            ip_origem=ip,
            utilizador_id=user.id,
            loja_id=user.loja_id,
            detalhe={"email": email},
        )
        self.db.commit()

        payload = self._user_to_payload(user)
        return TokenResponse(
            access_token=create_access_token(payload),
            refresh_token=create_refresh_token(payload),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=self._user_to_auth_info(user),
        )

    def refresh(self, refresh_token: str) -> RefreshTokenResponse:
        payload = decode_token(refresh_token, expected_type="refresh")

        user = self.repo.get_by_email(payload["email"])
        if user is None or not user.ativo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"detail": "Token inválido.", "code": "TOKEN_INVALID"},
            )

        new_payload = self._user_to_payload(user)
        return RefreshTokenResponse(
            access_token=create_access_token(new_payload),
            refresh_token=create_refresh_token(new_payload),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
