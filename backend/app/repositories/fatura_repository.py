from __future__ import annotations

from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import cast, Date
from app.models.fatura import Fatura
from app.models.ordem_servico import OrdemServico, OSPeca

class FaturaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, fatura_id: int) -> Fatura | None:
        return self.db.query(Fatura).options(
            joinedload(Fatura.ordem_servico).joinedload(OrdemServico.cliente),
            joinedload(Fatura.ordem_servico).joinedload(OrdemServico.trotinete),
            joinedload(Fatura.ordem_servico).joinedload(OrdemServico.loja),
            joinedload(Fatura.ordem_servico).joinedload(OrdemServico.pecas_aplicadas).joinedload(OSPeca.peca),
        ).filter(Fatura.id == fatura_id).first()

    def list(
        self,
        loja_id: int | None,
        ordem_servico_id: int | None,
        data_inicio: date | None,
        data_fim: date | None,
        page: int,
        page_size: int
    ) -> tuple[list[Fatura], int]:
        from app.models.cliente import Cliente
        query = self.db.query(Fatura).options(
            joinedload(Fatura.ordem_servico).joinedload(OrdemServico.cliente),
        ).join(OrdemServico)
        
        if loja_id is not None:
            query = query.filter(OrdemServico.loja_id == loja_id)
            
        if ordem_servico_id is not None:
            query = query.filter(Fatura.ordem_servico_id == ordem_servico_id)
            
        if data_inicio is not None:
            query = query.filter(cast(Fatura.data_emissao, Date) >= data_inicio)
            
        if data_fim is not None:
            query = query.filter(cast(Fatura.data_emissao, Date) <= data_fim)
            
        total = query.count()
        skip = (page - 1) * page_size
        itens = query.order_by(Fatura.data_emissao.desc()).offset(skip).limit(page_size).all()
        
        return itens, total

    def create(self, **kwargs) -> Fatura:
        fatura = Fatura(**kwargs)
        self.db.add(fatura)
        # O commit é feito no serviço para garantir a consistência da transação ACID (OS + Fatura + Auditoria)
        return fatura