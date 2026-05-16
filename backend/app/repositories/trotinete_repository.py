from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.trotinete import Trotinete
from app.models.ordem_servico import OrdemServico
from app.models.cliente import Cliente

class TrotineteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, trotinete_id: int) -> Trotinete | None:
        return self.db.query(Trotinete).filter(Trotinete.id == trotinete_id).first()

    def list(self, loja_id: int | None, cliente_id: int | None, numero_serie: str | None, skip: int, limit: int) -> tuple[list[Trotinete], int]:
        query = self.db.query(Trotinete)
        
        if loja_id is not None:
            query = query.join(Cliente).filter(Cliente.loja_id == loja_id)
        if cliente_id is not None:
            query = query.filter(Trotinete.cliente_id == cliente_id)
        if numero_serie is not None:
            query = query.filter(Trotinete.numero_serie == numero_serie)
            
        total = query.count()
        itens = query.offset(skip).limit(limit).all()
        return itens, total

    def list_by_cliente(self, cliente_id: int) -> list[Trotinete]:
        return self.db.query(Trotinete).filter(Trotinete.cliente_id == cliente_id).all()

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