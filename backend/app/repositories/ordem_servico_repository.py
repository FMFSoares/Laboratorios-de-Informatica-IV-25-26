from __future__ import annotations

from datetime import datetime, timezone, date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import cast, Date
from app.models.ordem_servico import OrdemServico, OSPeca, RegistoTempo, EstadoOrdemServico, OrdemServicoObservacao

class OrdemServicoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, os_id: int) -> OrdemServico | None:
        return self.db.query(OrdemServico).options(
            joinedload(OrdemServico.cliente),
            joinedload(OrdemServico.trotinete),
            joinedload(OrdemServico.mecanico),
            joinedload(OrdemServico.pecas_aplicadas).joinedload(OSPeca.peca),
            joinedload(OrdemServico.registos_tempo),
            joinedload(OrdemServico.observacoes).joinedload(OrdemServicoObservacao.autor),
        ).filter(OrdemServico.id == os_id).first()

    def list_by_cliente(self, cliente_id: int) -> list[OrdemServico]:
        return self.db.query(OrdemServico).options(
            joinedload(OrdemServico.trotinete),
            joinedload(OrdemServico.fatura),
        ).filter(OrdemServico.cliente_id == cliente_id).order_by(OrdemServico.data_entrada.desc()).all()

    def list(
        self, loja_id: int | None, estado: EstadoOrdemServico | None,
        mecanico_id: int | None, data_inicio: date | None,
        data_fim: date | None, skip: int, limit: int,
        exclude_timer_not_for: int | None = None,
    ) -> tuple[list[OrdemServico], int]:
        from app.models.loja import Loja
        from sqlalchemy import exists
        query = self.db.query(OrdemServico).options(
            joinedload(OrdemServico.cliente),
            joinedload(OrdemServico.trotinete),
            joinedload(OrdemServico.mecanico),
            joinedload(OrdemServico.loja),
        )

        if loja_id is not None:
            query = query.filter(OrdemServico.loja_id == loja_id)
        if estado is not None:
            query = query.filter(OrdemServico.estado == estado)
        if mecanico_id is not None:
            query = query.filter(OrdemServico.mecanico_id == mecanico_id)
        if data_inicio is not None:
            query = query.filter(cast(OrdemServico.data_entrada, Date) >= data_inicio)
        if data_fim is not None:
            query = query.filter(cast(OrdemServico.data_entrada, Date) <= data_fim)
        if exclude_timer_not_for is not None:
            query = query.filter(
                ~exists().where(
                    (RegistoTempo.ordem_servico_id == OrdemServico.id) &
                    (RegistoTempo.fim == None) &
                    (RegistoTempo.mecanico_id != exclude_timer_not_for)
                )
            )

        total = query.count()
        itens = query.order_by(OrdemServico.data_entrada.desc()).offset(skip).limit(limit).all()
        return itens, total

    def create(self, **kwargs) -> OrdemServico:
        os = OrdemServico(**kwargs)
        self.db.add(os)
        self.db.flush()  # Obtém o ID sem fechar a transação global
        os.numero = f"OS-{datetime.now(timezone.utc).year}-{os.id:04d}"
        return os

    def adicionar_peca_os(self, os_id: int, peca_id: int, quantidade: int, preco_venda_unitario: float) -> OSPeca:
        os_peca = OSPeca(ordem_servico_id=os_id, peca_id=peca_id, quantidade=quantidade, preco_venda_unitario=preco_venda_unitario)
        self.db.add(os_peca)
        return os_peca

    def get_peca_os(self, os_id: int, peca_id: int) -> OSPeca | None:
        return self.db.query(OSPeca).filter(OSPeca.ordem_servico_id == os_id, OSPeca.peca_id == peca_id).first()

    def remover_peca_os(self, os_peca: OSPeca) -> None:
        self.db.delete(os_peca)

    def create_observacao(self, os_id: int, autor_id: int, texto: str, criado_em) -> OrdemServicoObservacao:
        obs = OrdemServicoObservacao(
            ordem_servico_id=os_id,
            autor_id=autor_id,
            texto=texto,
            criado_em=criado_em,
        )
        self.db.add(obs)
        return obs