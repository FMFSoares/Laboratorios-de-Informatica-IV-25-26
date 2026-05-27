from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.auditoria_repository import AuditoriaRepository
from app.repositories.utilizador_repository import UtilizadorRepository
from app.repositories.loja_repository import LojaRepository
from app.schemas.auditoria import TipoEventoAuditoria
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.utilizador import UtilizadorCreate, UtilizadorUpdate, PasswordResetRequest, UtilizadorResponse, PerfilUtilizador
from app.core.security import hash_password

class UtilizadorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UtilizadorRepository(db)
        self.loja_repo = LojaRepository(db)
        self.auditoria_repo = AuditoriaRepository(db)

    def listar_utilizadores(self, page: int, page_size: int) -> PaginatedResponse[UtilizadorResponse]:
        skip = (page - 1) * page_size
        itens, total = self.repo.list(skip, page_size)
        pages = max(1, -(-total // page_size))

        def _to_response(u):
            data = {k: v for k, v in u.__dict__.items() if not k.startswith("_")}
            data["loja_nome"] = u.loja.nome if u.loja else None
            return UtilizadorResponse(**data)

        return PaginatedResponse[UtilizadorResponse](
            data=[_to_response(u) for u in itens],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    def _validar_perfil_loja_comissao(self, perfil: PerfilUtilizador, loja_id, comissao):
        """Validates loja_id and comissao constraints based on perfil."""
        if perfil != PerfilUtilizador.ADMINISTRADOR and not loja_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"detail": f"loja_id é obrigatório para o perfil {perfil.value}.", "code": "VALIDATION_ERROR"},
            )
        if perfil != PerfilUtilizador.MECANICO and comissao:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"detail": "O campo comissao só é permitido para o perfil MECANICO.", "code": "VALIDATION_ERROR"},
            )

    def criar_utilizador(self, body: UtilizadorCreate, current_user=None) -> DataResponse[UtilizadorResponse]:
        if self.repo.exists_email(body.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"detail": "Email já registado no sistema.", "code": "DUPLICATE_ENTRY"},
            )

        self._validar_perfil_loja_comissao(body.perfil, body.loja_id, body.comissao)

        if body.loja_id:
            loja = self.loja_repo.get_by_id(body.loja_id)
            if not loja:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"detail": "Loja não encontrada.", "code": "RESOURCE_NOT_FOUND"},
                )

        novo = self.repo.create(
            nome=body.nome,
            email=body.email,
            password_hash=hash_password(body.password),
            perfil=body.perfil,
            loja_id=body.loja_id,
            ativo=body.ativo,
            comissao=body.comissao if body.perfil == PerfilUtilizador.MECANICO else None,
            salario_base=body.salario_base,
        )

        data = {k: v for k, v in novo.__dict__.items() if not k.startswith("_")}
        data["loja_nome"] = novo.loja.nome if novo.loja else None

        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.UTILIZADOR_CRIADO,
            descricao=f"Utilizador '{body.nome}' ({body.perfil.value}) criado",
            utilizador_id=current_user.id if current_user else None,
            detalhe={"nome": body.nome, "email": body.email, "perfil": body.perfil.value, "loja_id": body.loja_id},
        )
        self.db.commit()

        return DataResponse[UtilizadorResponse](
            data=UtilizadorResponse(**data),
            message="Utilizador criado com sucesso.",
        )

    def obter_utilizador(self, utilizador_id: int) -> DataResponse[UtilizadorResponse]:
        u = self.repo.get_by_id(utilizador_id)
        if not u:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail={"detail": "Utilizador não encontrado.", "code": "RESOURCE_NOT_FOUND"})
        return DataResponse[UtilizadorResponse](data=self._to_response(u))

    def _to_response(self, u) -> UtilizadorResponse:
        data = {k: v for k, v in u.__dict__.items() if not k.startswith("_")}
        data["loja_nome"] = u.loja.nome if u.loja else None
        return UtilizadorResponse(**data)

    def atualizar_utilizador(self, utilizador_id: int, body: UtilizadorUpdate, current_user=None) -> DataResponse[UtilizadorResponse]:
        u = self.repo.get_by_id(utilizador_id)
        if not u:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail={"detail": "Utilizador não encontrado.", "code": "RESOURCE_NOT_FOUND"})

        updates = body.model_dump(exclude_unset=True)

        # If email is changing, check for duplicates
        if "email" in updates and updates["email"].lower() != u.email.lower():
            if self.repo.exists_email(updates["email"]):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail={"detail": "Email já registado.", "code": "DUPLICATE_ENTRY"})

        novo_perfil = updates.get("perfil", u.perfil)
        nova_loja   = updates.get("loja_id", u.loja_id)
        nova_comissao = updates.get("comissao", u.comissao)
        self._validar_perfil_loja_comissao(novo_perfil, nova_loja, nova_comissao)

        if "loja_id" in updates and updates["loja_id"]:
            if not self.loja_repo.get_by_id(updates["loja_id"]):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail={"detail": "Loja não encontrada.", "code": "RESOURCE_NOT_FOUND"})

        # Clear comissao if profile is no longer MECANICO
        if novo_perfil != PerfilUtilizador.MECANICO:
            updates["comissao"] = None

        u = self.repo.update(u, **updates)

        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.UTILIZADOR_ATUALIZADO,
            descricao=f"Utilizador '{u.nome}' atualizado",
            utilizador_id=current_user.id if current_user else None,
            detalhe={"utilizador_id": utilizador_id, "campos": list(updates.keys())},
        )
        self.db.commit()

        return DataResponse[UtilizadorResponse](data=self._to_response(u), message="Utilizador actualizado.")

    def alterar_password(self, utilizador_id: int, body: PasswordResetRequest, current_user=None) -> DataResponse[UtilizadorResponse]:
        u = self.repo.get_by_id(utilizador_id)
        if not u:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail={"detail": "Utilizador não encontrado.", "code": "RESOURCE_NOT_FOUND"})
        u = self.repo.update(u, password_hash=hash_password(body.nova_password))

        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.UTILIZADOR_PASSWORD_ALTERADA,
            descricao=f"Password do utilizador '{u.nome}' redefinida pelo administrador",
            utilizador_id=current_user.id if current_user else None,
            detalhe={"utilizador_id": utilizador_id},
        )
        self.db.commit()

        return DataResponse[UtilizadorResponse](data=self._to_response(u), message="Password alterada com sucesso.")
