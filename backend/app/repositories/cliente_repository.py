from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate


class ClienteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, cliente_id: int):
        return self.db.query(Cliente).filter(Cliente.id == cliente_id).first()

    def get_by_nif(self, nif: str):
        return self.db.query(Cliente).filter(Cliente.nif == nif).first()

    def get_all(self, skip: int = 0, limit: int = 100, loja_id: int | None = None, query_str: str | None = None):
        query = self.db.query(Cliente)
        if loja_id is not None:
            query = query.filter(Cliente.loja_id == loja_id)
        if query_str:
            like = f"%{query_str}%"
            query = query.filter(
                Cliente.nome.ilike(like) |
                Cliente.nif.ilike(like) |
                Cliente.telemovel.ilike(like) |
                Cliente.email.ilike(like)
            )
        return query.offset(skip).limit(limit).all()

    def count(self, loja_id: int | None = None, query_str: str | None = None) -> int:
        query = self.db.query(Cliente)
        if loja_id is not None:
            query = query.filter(Cliente.loja_id == loja_id)
        if query_str:
            like = f"%{query_str}%"
            query = query.filter(
                Cliente.nome.ilike(like) |
                Cliente.nif.ilike(like) |
                Cliente.telemovel.ilike(like) |
                Cliente.email.ilike(like)
            )
        return query.count()

    def update(self, cliente_id: int, data: dict):
        obj = self.db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def create(self, cliente_in: ClienteCreate, loja_id: int):
        db_obj = Cliente(**cliente_in.model_dump(), loja_id=loja_id, data_registo=datetime.now(timezone.utc))
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj