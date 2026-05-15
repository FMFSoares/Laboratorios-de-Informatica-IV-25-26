from __future__ import annotations

from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from app.models.ordem_servico import OrdemServico, EstadoOrdemServico
from app.models.fatura import Fatura
from app.models.stock import StockLoja
from app.models.peca import Peca
from app.models.loja import Loja
from app.models.utilizador import Utilizador
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse
from app.schemas.dashboard import (
    DashboardPeriodo,
    DashboardResponse,
    EficienciaMecanico,
    OrdensConcluidasPorLoja,
    PecaAbaixoStockMinimo,
)
from app.schemas.utilizador import PerfilUtilizador as P


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def obter(
        self,
        loja_id: int | None,
        data_inicio: date | None,
        data_fim: date | None,
        current_user: CurrentUserResponse,
    ) -> DataResponse[DashboardResponse]:
        hoje = date.today()
        d_inicio = data_inicio or (hoje - timedelta(days=30))
        d_fim = data_fim or hoje

        loja_filtro = loja_id if current_user.perfil == P.ADMINISTRADOR else current_user.loja_id

        # 1. Filtro Global de OS por datas
        os_query = self.db.query(OrdemServico).filter(
            cast(OrdemServico.data_entrada, Date) >= d_inicio,
            cast(OrdemServico.data_entrada, Date) <= d_fim
        )
        if loja_filtro is not None:
            os_query = os_query.filter(OrdemServico.loja_id == loja_filtro)

        # Métrica 1: Ordens por estado
        estado_counts = os_query.with_entities(OrdemServico.estado, func.count(OrdemServico.id)).group_by(OrdemServico.estado).all()
        ordens_por_estado = {estado.value: 0 for estado in EstadoOrdemServico}
        for estado, count in estado_counts:
            ordens_por_estado[estado.value] = count

        # Métrica 2: Ordens Concluídas por Loja (Ordenação nativa pelo topo)
        concluidas_query = self.db.query(
            Loja.id, Loja.nome, func.count(OrdemServico.id).label("total")
        ).join(OrdemServico, Loja.id == OrdemServico.loja_id)\
         .filter(
             OrdemServico.estado.in_([EstadoOrdemServico.CONCLUIDA, EstadoOrdemServico.FATURADA]),
             cast(OrdemServico.data_entrada, Date) >= d_inicio,
             cast(OrdemServico.data_entrada, Date) <= d_fim
         )
        if loja_filtro is not None:
            concluidas_query = concluidas_query.filter(Loja.id == loja_filtro)

        concluidas_por_loja_raw = concluidas_query.group_by(Loja.id).order_by(func.count(OrdemServico.id).desc()).all()
        ordens_concluidas_por_loja = [
            OrdensConcluidasPorLoja(loja_id=r[0], loja_nome=r[1], total=r[2]) for r in concluidas_por_loja_raw
        ]

        # Métrica 3: Tempo Médio de Reparação Geral
        tempo_medio = os_query.with_entities(func.avg(OrdemServico.tempo_total_minutos)).filter(OrdemServico.tempo_total_minutos.isnot(None)).scalar()
        tempo_medio_reparacao_minutos = int(tempo_medio) if tempo_medio else None

        # Métrica 4: Faturação Total
        fat_query = self.db.query(func.sum(Fatura.valor_final)).join(OrdemServico)\
            .filter(cast(Fatura.data_emissao, Date) >= d_inicio, cast(Fatura.data_emissao, Date) <= d_fim)
        if loja_filtro is not None:
            fat_query = fat_query.filter(OrdemServico.loja_id == loja_filtro)

        faturacao_total = fat_query.scalar() or 0.0

        # Métrica 5: Peças abaixo do stock mínimo
        stock_query = self.db.query(StockLoja, Peca, Loja).join(Peca).join(Loja)\
            .filter(StockLoja.quantidade < StockLoja.limite_minimo)
        if loja_filtro is not None:
            stock_query = stock_query.filter(StockLoja.loja_id == loja_filtro)

        stock_alertas = stock_query.order_by((StockLoja.quantidade - StockLoja.limite_minimo).asc()).all()
        pecas_abaixo_stock = [
            PecaAbaixoStockMinimo(
                peca_id=s.StockLoja.peca_id, peca_nome=s.Peca.nome,
                loja_id=s.StockLoja.loja_id, loja_nome=s.Loja.nome,
                quantidade=s.StockLoja.quantidade, limite_minimo=s.StockLoja.limite_minimo
            ) for s in stock_alertas
        ]

        # Métrica 6: Eficiência por Mecânico (Ordenação nativa pelo topo)
        mecanicos_query = self.db.query(
            Utilizador.id, Utilizador.nome,
            func.count(OrdemServico.id).label("total_ordens"),
            func.avg(OrdemServico.tempo_total_minutos).label("media_minutos")
        ).join(OrdemServico, Utilizador.id == OrdemServico.mecanico_id)\
         .filter(
             OrdemServico.estado.in_([EstadoOrdemServico.CONCLUIDA, EstadoOrdemServico.FATURADA]),
             cast(OrdemServico.data_entrada, Date) >= d_inicio,
             cast(OrdemServico.data_entrada, Date) <= d_fim
         )
        if loja_filtro is not None:
            mecanicos_query = mecanicos_query.filter(OrdemServico.loja_id == loja_filtro)

        mecanicos_stats = mecanicos_query.group_by(Utilizador.id).order_by(func.count(OrdemServico.id).desc()).all()
        eficiencia = [
            EficienciaMecanico(
                mecanico_id=m[0], nome=m[1], ordens_concluidas=m[2], tempo_medio_minutos=int(m[3]) if m[3] else None
            ) for m in mecanicos_stats
        ]

        return DataResponse[DashboardResponse](
            data=DashboardResponse(
                periodo=DashboardPeriodo(inicio=d_inicio, fim=d_fim),
                ordens_por_estado=ordens_por_estado,
                ordens_concluidas_por_loja=ordens_concluidas_por_loja,
                tempo_medio_reparacao_minutos=tempo_medio_reparacao_minutos,
                faturacao_total=faturacao_total,
                pecas_abaixo_stock_minimo=pecas_abaixo_stock,
                eficiencia_por_mecanico=eficiencia,
            )
        )
