from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.auditoria import Auditoria
from app.schemas.auditoria import TipoEventoAuditoria


class AuditoriaRepository:
    def __init__(self, db: Session):
        self.db = db

    def registar(
        self,
        evento: TipoEventoAuditoria,
        descricao: str,
        ip_origem: str | None = None,
        utilizador_id: int | None = None,
        utilizador_nome: str | None = None,  # Mantido para compatibilidade com o interface mas ignorado pois o modelo apenas precisa da FK
        loja_id: int | None = None,
        detalhe: dict | None = None,
    ) -> Auditoria:
        novo_evento = Auditoria(
            evento=evento,
            descricao=descricao,
            ip_origem=ip_origem,
            utilizador_id=utilizador_id,
            loja_id=loja_id,
            detalhe=detalhe or {},
            timestamp=datetime.now(timezone.utc)
        )
        self.db.add(novo_evento)
        return novo_evento

    def listar(
        self,
        loja_id: int | None = None,
        evento: str | None = None,
        utilizador_id: int | None = None,
        data_inicio=None,
        data_fim=None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Auditoria], int]:
        query = self.db.query(Auditoria).options(joinedload(Auditoria.utilizador))
        
        if loja_id is not None:
            query = query.filter(Auditoria.loja_id == loja_id)
        if evento is not None:
            query = query.filter(Auditoria.evento == evento)
        if utilizador_id is not None:
            query = query.filter(Auditoria.utilizador_id == utilizador_id)
        if data_inicio is not None:
            query = query.filter(func.date(Auditoria.timestamp) >= data_inicio)
        if data_fim is not None:
            query = query.filter(func.date(Auditoria.timestamp) <= data_fim)
            
        total = query.count()
        skip = (page - 1) * page_size
        # Ordena sempre pelos mais recentes primeiro
        itens = query.order_by(Auditoria.timestamp.desc()).offset(skip).limit(page_size).all()
        
        return itens, total

    def listar_por_os(self, os_id: int) -> list[Auditoria]:
        return (
            self.db.query(Auditoria)
            .options(joinedload(Auditoria.utilizador))
            .filter(func.json_extract(Auditoria.detalhe, '$.os_id') == os_id)
            .order_by(Auditoria.timestamp.desc())
            .all()
        )
