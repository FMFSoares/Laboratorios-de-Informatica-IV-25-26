from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload, contains_eager
from app.models.trotinete import Trotinete
from app.models.ordem_servico import OrdemServico
from app.models.cliente import Cliente

class TrotineteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, trotinete_id: int) -> Trotinete | None:
        return (
            self.db.query(Trotinete)
            .join(Cliente, Trotinete.cliente_id == Cliente.id)
            .options(contains_eager(Trotinete.cliente))
            .filter(Trotinete.id == trotinete_id)
            .first()
        )

    def list(
        self,
        loja_id: int | None,
        cliente_id: int | None,
        query_str: str | None,
        skip: int,
        limit: int,
    ) -> tuple[list[Trotinete], int]:
        # Always JOIN cliente — used for filtering and eager loading.
        # Using contains_eager avoids mixing joinedload + explicit join,
        # which causes SQLAlchemy to emit an unreliable count() subquery.
        q = (
            self.db.query(Trotinete)
            .join(Cliente, Trotinete.cliente_id == Cliente.id)
        )

        if loja_id is not None:
            q = q.filter(Cliente.loja_id == loja_id)
        if cliente_id is not None:
            q = q.filter(Trotinete.cliente_id == cliente_id)
        if query_str:
            like = f"%{query_str}%"
            q = q.filter(
                or_(
                    Trotinete.numero_serie.ilike(like),
                    Trotinete.marca.ilike(like),
                    Trotinete.modelo.ilike(like),
                    Cliente.nome.ilike(like),
                )
            )

        total = q.count()
        itens = q.options(contains_eager(Trotinete.cliente)).offset(skip).limit(limit).all()
        return itens, total

    def list_by_cliente(self, cliente_id: int) -> list[Trotinete]:
        return (
            self.db.query(Trotinete)
            .join(Cliente, Trotinete.cliente_id == Cliente.id)
            .options(contains_eager(Trotinete.cliente))
            .filter(Trotinete.cliente_id == cliente_id)
            .all()
        )

    def exists_numero_serie(self, numero_serie: str) -> bool:
        return self.db.query(Trotinete.id).filter(Trotinete.numero_serie == numero_serie).first() is not None

    def create(self, **kwargs) -> Trotinete:
        nova = Trotinete(**kwargs, data_registo=datetime.now(timezone.utc))
        self.db.add(nova)
        self.db.commit()
        self.db.refresh(nova)
        return nova

    def count_by_trotinete(self, trotinete_id: int) -> int:
        return self.db.query(OrdemServico).filter(OrdemServico.trotinete_id == trotinete_id).count()