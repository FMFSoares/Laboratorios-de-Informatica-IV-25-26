from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.utilizador_repository import UtilizadorRepository
from app.repositories.loja_repository import LojaRepository
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.utilizador import UtilizadorCreate, UtilizadorResponse
from app.core.security import hash_password

class UtilizadorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UtilizadorRepository(db)
        self.loja_repo = LojaRepository(db)

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

    def criar_utilizador(self, body: UtilizadorCreate) -> DataResponse[UtilizadorResponse]:
        if self.repo.exists_email(body.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"detail": "Email já registado no sistema.", "code": "DUPLICATE_ENTRY"},
            )

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
        )

        data = {k: v for k, v in novo.__dict__.items() if not k.startswith("_")}
        data["loja_nome"] = novo.loja.nome if novo.loja else None

        return DataResponse[UtilizadorResponse](
            data=UtilizadorResponse(**data),
            message="Utilizador criado com sucesso.",
        )
