from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate


class ClienteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, cliente_id: int) -> Cliente | None:
        return self.db.query(Cliente).filter(Cliente.id == cliente_id).first()

    def get_by_nif(self, nif: str) -> Cliente | None:
        return self.db.query(Cliente).filter(Cliente.nif == nif).first()

    def get_all(self, skip: int = 0, limit: int = 100, loja_id: int | None = None, query_str: str | None = None) -> list[Cliente]:
        query = self.db.query(Cliente)
        if loja_id is not None:
            query = query.filter(Cliente.loja_id == loja_id)
        if query_str:
            query = query.filter((Cliente.nif == query_str) | (Cliente.telemovel == query_str))
        return query.offset(skip).limit(limit).all()

    def count(self, loja_id: int | None = None, query_str: str | None = None) -> int:
        query = self.db.query(Cliente)
        if loja_id is not None:
            query = query.filter(Cliente.loja_id == loja_id)
        if query_str:
            query = query.filter((Cliente.nif == query_str) | (Cliente.telemovel == query_str))
        return query.count()

    def create(self, cliente_in: ClienteCreate, loja_id: int) -> Cliente:
        # Transforma o Pydantic num modelo SQLAlchemy
        db_obj = Cliente(**cliente_in.model_dump(), loja_id=loja_id, data_registo=datetime.now(timezone.utc))
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj