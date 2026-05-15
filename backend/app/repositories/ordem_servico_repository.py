from datetime import datetime, timezone, date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import cast, Date
from app.models.ordem_servico import OrdemServico, OSPeca, RegistoTempo, EstadoOrdemServico

class OrdemServicoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, os_id: int) -> OrdemServico | None:
        return self.db.query(OrdemServico).options(
            joinedload(OrdemServico.cliente),
            joinedload(OrdemServico.trotinete),
            joinedload(OrdemServico.mecanico),
            joinedload(OrdemServico.pecas_usadas).joinedload(OSPeca.peca),
            joinedload(OrdemServico.registos_tempo)
        ).filter(OrdemServico.id == os_id).first()

    def list(
        self, loja_id: int | None, estado: EstadoOrdemServico | None,
        mecanico_id: int | None, data_inicio: date | None,
        data_fim: date | None, skip: int, limit: int
    ) -> tuple[list[OrdemServico], int]:
        query = self.db.query(OrdemServico).options(
            joinedload(OrdemServico.cliente),
            joinedload(OrdemServico.trotinete),
            joinedload(OrdemServico.mecanico)
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