from __future__ import annotations

from sqlalchemy.orm import Session, joinedload
from app.models.utilizador import Utilizador
from app.schemas.utilizador import PerfilUtilizador

class UtilizadorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, utilizador_id: int) -> Utilizador | None:
        return self.db.query(Utilizador).options(joinedload(Utilizador.loja)).filter(Utilizador.id == utilizador_id).first()

    def get_by_email(self, email: str) -> Utilizador | None:
        return self.db.query(Utilizador).options(joinedload(Utilizador.loja)).filter(Utilizador.email.ilike(email)).first()

    def list(self, skip: int, limit: int) -> tuple[list[Utilizador], int]:
        query = self.db.query(Utilizador).options(joinedload(Utilizador.loja))
        total = query.count()
        itens = query.offset(skip).limit(limit).all()
        return itens, total

    def list_by_perfil(self, perfil: PerfilUtilizador, loja_id: int | None = None) -> list[Utilizador]:
        query = self.db.query(Utilizador).filter(Utilizador.perfil == perfil)
        if loja_id is not None:
            query = query.filter(Utilizador.loja_id == loja_id)
        return query.all()

    def exists_email(self, email: str) -> bool:
        return self.db.query(Utilizador.id).filter(Utilizador.email.ilike(email)).first() is not None

    def create(self, **kwargs) -> Utilizador:
        novo = Utilizador(**kwargs)
        self.db.add(novo)
        self.db.commit()
        self.db.refresh(novo)
        return novo

    def update(self, utilizador: Utilizador, **kwargs) -> Utilizador:
        for k, v in kwargs.items():
            setattr(utilizador, k, v)
        self.db.commit()
        self.db.refresh(utilizador)
        return utilizador