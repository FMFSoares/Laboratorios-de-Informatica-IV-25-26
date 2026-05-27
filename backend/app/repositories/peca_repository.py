from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.peca import Peca
from app.schemas.peca import CategoriaPeca

class PecaRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_id(self, peca_id: int) -> Peca | None:
        return self.db.query(Peca).filter(Peca.id == peca_id).first()

    def list(
        self,
        query: str | None,
        categoria: CategoriaPeca | None,
        skip: int,
        limit: int,
        incluir_inativos: bool = False,
    ) -> tuple[list[Peca], int]:
        query_obj = self.db.query(Peca)
        if not incluir_inativos:
            query_obj = query_obj.filter(Peca.ativo == True)
        if categoria:
            query_obj = query_obj.filter(Peca.categoria == categoria)
        if query:
            query_obj = query_obj.filter(
                or_(
                    Peca.nome.ilike(f"%{query}%"),
                    Peca.referencia.ilike(f"%{query}%")
                )
            )
            
        total = query_obj.count()
        itens = query_obj.offset(skip).limit(limit).all()
        return itens, total

    def exists_referencia(self, referencia: str) -> bool:
        return self.db.query(Peca.id).filter(Peca.referencia == referencia).first() is not None

    def create(self, **kwargs) -> Peca:
        kwargs['ativo'] = kwargs.get('ativo', True)
        nova = Peca(**kwargs)
        self.db.add(nova)
        self.db.commit()
        self.db.refresh(nova)
        return nova

    def update(self, peca: Peca, **kwargs) -> Peca:
        for k, v in kwargs.items():
            setattr(peca, k, v)
        self.db.commit()
        self.db.refresh(peca)
        return peca
