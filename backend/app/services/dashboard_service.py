from __future__ import annotations

# [pendente de integração com BD]
# Métricas calculadas sobre os mocks em memória para a Etapa 3.

from datetime import date, timedelta

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


def obter(
    loja_id: int | None,
    data_inicio: date | None,
    data_fim: date | None,
    current_user: CurrentUserResponse,
) -> DataResponse[DashboardResponse]:
    from app.services.ordem_servico_service import _MOCK_OS
    from app.services.fatura_service import _MOCK_FATURAS
    from app.services.stock_service import _MOCK_STOCK, _MOCK_LOJAS
    from app.services.peca_service import _MOCK_PECAS
    from app.services.auth_service import _MOCK_USERS
    from app.schemas.ordem_servico import EstadoOrdemServico as E

    hoje = date.today()
    d_inicio = data_inicio or (hoje - timedelta(days=30))
    d_fim = data_fim or hoje

    # Loja a filtrar: ADMIN pode especificar loja_id, os outros vêem sempre a sua
    loja_filtro = loja_id if current_user.perfil == P.ADMINISTRADOR else current_user.loja_id

    # OS no período (e loja se aplicável)
    os_filtradas = [
        o for o in _MOCK_OS
        if d_inicio <= o["data_entrada"].date() <= d_fim
    ]
    if loja_filtro is not None:
        os_filtradas = [o for o in os_filtradas if o["loja_id"] == loja_filtro]

    # ordens_por_estado
    estados: dict[str, int] = {e.value: 0 for e in E}
    for o in os_filtradas:
        estados[o["estado"].value] += 1

    # ordens_concluidas_por_loja
    concluidas_map: dict[int, int] = {}
    for o in os_filtradas:
        if o["estado"] in {E.CONCLUIDA, E.FATURADA}:
            concluidas_map[o["loja_id"]] = concluidas_map.get(o["loja_id"], 0) + 1
    ordens_concluidas_por_loja = [
        OrdensConcluidasPorLoja(
            loja_id=lid,
            loja_nome=_MOCK_LOJAS.get(lid, f"Loja {lid}"),
            total=total,
        )
        for lid, total in sorted(concluidas_map.items())
    ]

    # tempo_medio_reparacao_minutos
    tempos = [o["tempo_total_minutos"] for o in os_filtradas if o["tempo_total_minutos"] is not None]
    tempo_medio = int(sum(tempos) / len(tempos)) if tempos else None

    # faturacao_total — faturas emitidas no período
    faturas_periodo = [
        f for f in _MOCK_FATURAS
        if d_inicio <= f["data_emissao"].date() <= d_fim
    ]
    if loja_filtro is not None:
        faturas_periodo = [f for f in faturas_periodo if f["loja_id"] == loja_filtro]
    faturacao_total = round(sum(f["valor_final"] for f in faturas_periodo), 2)

    # pecas_abaixo_stock_minimo
    pecas_dict = {p["id"]: p for p in _MOCK_PECAS}
    pecas_alerta = []
    for s in _MOCK_STOCK:
        if loja_filtro is not None and s["loja_id"] != loja_filtro:
            continue
        if s["quantidade"] < s["limite_minimo"]:
            peca = pecas_dict.get(s["peca_id"])
            pecas_alerta.append(PecaAbaixoStockMinimo(
                peca_id=s["peca_id"],
                peca_nome=peca["nome"] if peca else f"Peça {s['peca_id']}",
                loja_id=s["loja_id"],
                loja_nome=_MOCK_LOJAS.get(s["loja_id"], f"Loja {s['loja_id']}"),
                quantidade=s["quantidade"],
                limite_minimo=s["limite_minimo"],
            ))

    # eficiencia_por_mecanico — só mecânicos com OS concluídas no período
    mecanicos = {u["id"]: u for u in _MOCK_USERS if u["perfil"] == P.MECANICO}
    eficiencia_map: dict[int, list] = {mid: [] for mid in mecanicos}
    for o in os_filtradas:
        if o["estado"] in {E.CONCLUIDA, E.FATURADA} and o["mecanico_id"] in eficiencia_map:
            eficiencia_map[o["mecanico_id"]].append(o["tempo_total_minutos"])

    eficiencia_por_mecanico = []
    for mid, tempos_m in eficiencia_map.items():
        if not tempos_m:
            continue
        t_validos = [t for t in tempos_m if t is not None]
        eficiencia_por_mecanico.append(EficienciaMecanico(
            mecanico_id=mid,
            nome=mecanicos[mid]["nome"],
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
