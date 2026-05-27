from __future__ import annotations

from sqlalchemy.orm import Session
from app.models.loja import Loja

class LojaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, loja_id: int) -> Loja | None:
        return self.db.query(Loja).filter(Loja.id == loja_id).first()

    def list(self, loja_id_filtro: int | None, skip: int, limit: int) -> tuple[list[Loja], int]:
        query = self.db.query(Loja)
        if loja_id_filtro is not None:
            query = query.filter(Loja.id == loja_id_filtro)
        
        total = query.count()
        itens = query.offset(skip).limit(limit).all()
        return itens, total

    def exists(self, loja_id: int) -> bool:
        return self.db.query(Loja.id).filter(Loja.id == loja_id).first() is not None

    def get_nome(self, loja_id: int) -> str | None:
        res = self.db.query(Loja.nome).filter(Loja.id == loja_id).first()
        return res[0] if res else None

    def get_telefone(self, loja_id: int) -> str | None:
        res = self.db.query(Loja.telefone).filter(Loja.id == loja_id).first()
        return res[0] if res else None

    def as_dict(self, loja_id: int) -> dict | None:
        loja = self.get_by_id(loja_id)
        if loja:
            return {"nome": loja.nome, "morada": loja.morada, "telefone": loja.telefone}
        return None

    def create(self, **kwargs) -> "Loja":
        from app.models.loja import Loja as LojaModel
        nova = LojaModel(**kwargs)
        nova.ativo = kwargs.get("ativo", True)
        self.db.add(nova)
        self.db.commit()
        self.db.refresh(nova)
        return nova

    def update(self, loja, **kwargs):
        for k, v in kwargs.items():
            setattr(loja, k, v)
        self.db.commit()
        self.db.refresh(loja)
        return loja