from __future__ import annotations

from datetime import date, timedelta

from app.repositories.ordem_servico_repository import MockOrdemServicoRepository
from app.repositories.fatura_repository import MockFaturaRepository
from app.repositories.stock_repository import MockStockRepository
from app.repositories.peca_repository import MockPecaRepository
from app.repositories.utilizador_repository import MockUtilizadorRepository
from app.repositories.loja_repository import MockLojaRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse
from app.schemas.dashboard import (
    DashboardPeriodo,
    DashboardResponse,
    EficienciaMecanico,
    OrdensConcluidasPorLoja,
    PecaAbaixoStockMinimo,
)
from app.schemas.ordem_servico import EstadoOrdemServico as E
from app.schemas.utilizador import PerfilUtilizador as P

_os_repo = MockOrdemServicoRepository()
_fatura_repo = MockFaturaRepository()
_stock_repo = MockStockRepository()
_peca_repo = MockPecaRepository()
_util_repo = MockUtilizadorRepository()
_loja_repo = MockLojaRepository()


def obter(
    loja_id: int | None,
    data_inicio: date | None,
    data_fim: date | None,
    current_user: CurrentUserResponse,
) -> DataResponse[DashboardResponse]:
    hoje = date.today()
    d_inicio = data_inicio or (hoje - timedelta(days=30))
    d_fim = data_fim or hoje

    loja_filtro = loja_id if current_user.perfil == P.ADMINISTRADOR else current_user.loja_id

    os_todas = _os_repo.list_all()
    os_filtradas = [
        o for o in os_todas
        if d_inicio <= o.data_entrada.date() <= d_fim
        and (loja_filtro is None or o.loja_id == loja_filtro)
    ]

    # ordens_por_estado
    estados: dict[str, int] = {e.value: 0 for e in E}
    for o in os_filtradas:
        estados[o.estado.value] += 1

    # ordens_concluidas_por_loja
    concluidas_map: dict[int, int] = {}
    for o in os_filtradas:
        if o.estado in {E.CONCLUIDA, E.FATURADA}:
            concluidas_map[o.loja_id] = concluidas_map.get(o.loja_id, 0) + 1

    ordens_concluidas_por_loja = [
        OrdensConcluidasPorLoja(
            loja_id=lid,
            loja_nome=_loja_repo.get_nome(lid) or f"Loja {lid}",
            total=total,
        )
        for lid, total in sorted(concluidas_map.items())
    ]

    # tempo_medio_reparacao_minutos
    tempos = [o.tempo_total_minutos for o in os_filtradas if o.tempo_total_minutos is not None]
    tempo_medio = int(sum(tempos) / len(tempos)) if tempos else None

    # faturacao_total
    faturas_periodo = [
        f for f in _fatura_repo.list_all()
        if d_inicio <= f.data_emissao.date() <= d_fim
        and (loja_filtro is None or f.loja_id == loja_filtro)
    ]
    faturacao_total = round(sum(f.valor_final for f in faturas_periodo), 2)

    # pecas_abaixo_stock_minimo
    pecas_alerta = []
    for s in _stock_repo.list_all():
        if loja_filtro is not None and s.loja_id != loja_filtro:
            continue
        if s.quantidade < s.limite_minimo:
            peca = _peca_repo.get_by_id(s.peca_id)
            pecas_alerta.append(PecaAbaixoStockMinimo(
                peca_id=s.peca_id,
                peca_nome=peca.nome if peca else f"Peça {s.peca_id}",
                loja_id=s.loja_id,
                loja_nome=_loja_repo.get_nome(s.loja_id) or f"Loja {s.loja_id}",
                quantidade=s.quantidade,
                limite_minimo=s.limite_minimo,
            ))

    # eficiencia_por_mecanico
    mecanicos = {u.id: u for u in _util_repo.list_by_perfil(P.MECANICO)}
    eficiencia_map: dict[int, list] = {mid: [] for mid in mecanicos}

    for o in os_filtradas:
        if o.estado in {E.CONCLUIDA, E.FATURADA} and o.mecanico_id in eficiencia_map:
            eficiencia_map[o.mecanico_id].append(o.tempo_total_minutos)

    eficiencia_por_mecanico = []
    for mid, tempos_m in eficiencia_map.items():
        if not tempos_m:
            continue
        t_validos = [t for t in tempos_m if t is not None]
        eficiencia_por_mecanico.append(EficienciaMecanico(
            mecanico_id=mid,
            nome=mecanicos[mid].nome,
            ordens_concluidas=len(tempos_m),
            tempo_medio_minutos=int(sum(t_validos) / len(t_validos)) if t_validos else None,
        ))

    return DataResponse[DashboardResponse](
        data=DashboardResponse(
            periodo=DashboardPeriodo(inicio=d_inicio, fim=d_fim),
            ordens_por_estado=estados,
            ordens_concluidas_por_loja=ordens_concluidas_por_loja,
            tempo_medio_reparacao_minutos=tempo_medio,
            faturacao_total=faturacao_total,
            pecas_abaixo_stock_minimo=pecas_alerta,
            eficiencia_por_mecanico=eficiencia_por_mecanico,
        )
    )
