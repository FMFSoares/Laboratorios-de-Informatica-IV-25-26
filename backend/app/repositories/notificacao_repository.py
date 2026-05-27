from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.notificacao import Notificacao
from app.schemas.notificacao import TipoNotificacao


class NotificacaoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        utilizador_id: int,
        tipo: TipoNotificacao,
        titulo: str,
        mensagem: str,
        referencia_id: int | None = None,
        referencia_tipo: str | None = None,
    ) -> Notificacao:
        n = Notificacao(
            utilizador_id=utilizador_id,
            tipo=tipo,
            titulo=titulo,
            mensagem=mensagem,
            lida=False,
            data_criacao=datetime.now(timezone.utc),
            referencia_id=referencia_id,
            referencia_tipo=referencia_tipo,
        )
        self.db.add(n)
        return n

    def list(
        self, utilizador_id: int, apenas_nao_lidas: bool, skip: int, limit: int
    ) -> tuple[list[Notificacao], int]:
        query = self.db.query(Notificacao).filter(Notificacao.utilizador_id == utilizador_id)
        if apenas_nao_lidas:
            query = query.filter(Notificacao.lida == False)
        total = query.count()
        itens = query.order_by(Notificacao.data_criacao.desc()).offset(skip).limit(limit).all()
        return itens, total

    def get_by_id(self, notificacao_id: int) -> Notificacao | None:
        return self.db.query(Notificacao).filter(Notificacao.id == notificacao_id).first()

    def marcar_lida(self, notificacao_id: int) -> Notificacao | None:
        n = self.get_by_id(notificacao_id)
        if n:
            n.lida = True
        return n

    def marcar_todas_lidas(self, utilizador_id: int) -> None:
        self.db.query(Notificacao).filter(
            Notificacao.utilizador_id == utilizador_id,
            Notificacao.lida == False,
        ).update({"lida": True})

    def apagar_uma(self, notificacao_id: int) -> None:
        self.db.query(Notificacao).filter(Notificacao.id == notificacao_id).delete()

    def apagar_todas(self, utilizador_id: int) -> None:
        self.db.query(Notificacao).filter(Notificacao.utilizador_id == utilizador_id).delete()

    def count_nao_lidas(self, utilizador_id: int) -> int:
        return self.db.query(Notificacao).filter(
            Notificacao.utilizador_id == utilizador_id,
            Notificacao.lida == False,
        ).count()
