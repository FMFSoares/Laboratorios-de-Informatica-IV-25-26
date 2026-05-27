from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.notificacao_repository import NotificacaoRepository
from app.schemas.notificacao import TipoNotificacao, NotificacaoResponse
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import PaginatedResponse, DataResponse


def criar_notificacao(
    db: Session,
    utilizador_id: int,
    tipo: TipoNotificacao,
    titulo: str,
    mensagem: str,
    referencia_id: int | None = None,
    referencia_tipo: str | None = None,
) -> None:
    """Fire-and-forget helper. Caller is responsible for committing."""
    NotificacaoRepository(db).create(
        utilizador_id=utilizador_id,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        referencia_id=referencia_id,
        referencia_tipo=referencia_tipo,
    )


class NotificacaoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = NotificacaoRepository(db)

    def listar(
        self, page: int, page_size: int, apenas_nao_lidas: bool, current_user: CurrentUserResponse
    ) -> PaginatedResponse[NotificacaoResponse]:
        skip = (page - 1) * page_size
        itens, total = self.repo.list(current_user.id, apenas_nao_lidas, skip, page_size)
        pages = max(1, -(-total // page_size))
        return PaginatedResponse[NotificacaoResponse](
            data=[NotificacaoResponse.model_validate(n) for n in itens],
            total=total, page=page, page_size=page_size, pages=pages,
        )

    def count_nao_lidas(self, current_user: CurrentUserResponse) -> int:
        return self.repo.count_nao_lidas(current_user.id)

    def marcar_lida(self, notificacao_id: int, current_user: CurrentUserResponse) -> None:
        n = self.repo.get_by_id(notificacao_id)
        if not n:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificação não encontrada.")
        if n.utilizador_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")
        self.repo.marcar_lida(notificacao_id)
        self.db.commit()

    def marcar_todas_lidas(self, current_user: CurrentUserResponse) -> None:
        self.repo.marcar_todas_lidas(current_user.id)
        self.db.commit()

    def apagar_uma(self, notificacao_id: int, current_user: CurrentUserResponse) -> None:
        n = self.repo.get_by_id(notificacao_id)
        if not n:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificação não encontrada.")
        if n.utilizador_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")
        self.repo.apagar_uma(notificacao_id)
        self.db.commit()

    def apagar_todas(self, current_user: CurrentUserResponse) -> None:
        self.repo.apagar_todas(current_user.id)
        self.db.commit()
