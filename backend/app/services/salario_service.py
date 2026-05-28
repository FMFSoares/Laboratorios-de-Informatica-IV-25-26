from __future__ import annotations

from calendar import monthrange
from datetime import date

from sqlalchemy import func, cast, Date
from sqlalchemy.orm import Session

from app.models.fatura import Fatura
from app.models.ordem_servico import OrdemServico
from app.models.utilizador import Utilizador
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse
from app.schemas.salario import SalarioHistoricoItem, SalarioUtilizador
from app.schemas.utilizador import PerfilUtilizador as P


class SalarioService:
    def __init__(self, db: Session):
        self.db = db

    def calcular(
        self,
        ano: int,
        mes: int,
        current_user: CurrentUserResponse,
    ) -> DataResponse[list[SalarioUtilizador]]:
        inicio = date(ano, mes, 1)
        fim = date(ano, mes, monthrange(ano, mes)[1])

        # Build base query — GERENTE_LOJA sees only their store's workers
        q = self.db.query(Utilizador).filter(Utilizador.ativo == True)
        if current_user.perfil == P.GERENTE_LOJA:
            q = q.filter(Utilizador.loja_id == current_user.loja_id)
        workers = q.order_by(Utilizador.nome).all()

        # Pre-compute commission earned per mechanic in the period:
        # SUM(fatura.valor_final) grouped by mecanico_id for FATURADA faturas
        comissao_rows = (
            self.db.query(
                OrdemServico.mecanico_id,
                func.sum(Fatura.valor_final).label("total_faturado"),
            )
            .join(Fatura, Fatura.ordem_servico_id == OrdemServico.id)
            .filter(
                cast(Fatura.data_emissao, Date) >= inicio,
                cast(Fatura.data_emissao, Date) <= fim,
                OrdemServico.mecanico_id.isnot(None),
            )
            .group_by(OrdemServico.mecanico_id)
            .all()
        )
        faturado_por_mecanico: dict[int, float] = {
            row.mecanico_id: float(row.total_faturado) for row in comissao_rows
        }

        result = []
        for w in workers:
            base = float(w.salario_base or 0.0)
            comissao_ganha = 0.0
            if w.perfil == P.MECANICO and w.comissao:
                faturado = faturado_por_mecanico.get(w.id, 0.0)
                comissao_ganha = round(faturado * w.comissao / 100, 2)

            loja_nome = w.loja.nome if w.loja else None

            result.append(
                SalarioUtilizador(
                    id=w.id,
                    nome=w.nome,
                    perfil=w.perfil.value,
                    loja_id=w.loja_id,
                    loja_nome=loja_nome,
                    salario_base=base,
                    comissao_percentagem=w.comissao,
                    comissao_ganha=comissao_ganha,
                    total=round(base + comissao_ganha, 2),
                )
            )

        return DataResponse(data=result)

    def calcular_historico(
        self,
        utilizador_id: int,
        meses: int,
    ) -> DataResponse[list[SalarioHistoricoItem]]:
        from fastapi import HTTPException
        user = self.db.query(Utilizador).filter(Utilizador.id == utilizador_id).first()
        if not user:
            raise HTTPException(status_code=404, detail={"detail": "Utilizador não encontrado.", "code": "NOT_FOUND"})

        MESES_PT = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                    "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

        hoje = date.today()
        # Compute start of the oldest month we need
        total_months_now = hoje.year * 12 + hoje.month - 1
        oldest = total_months_now - meses + 1
        ano_inicio = oldest // 12
        mes_inicio = oldest % 12 + 1
        inicio_range = date(ano_inicio, mes_inicio, 1)

        # Single query: faturado per month for this mechanic across the full range
        faturado_por_mes: dict[tuple[int, int], float] = {}
        if user.perfil == P.MECANICO and user.comissao:
            rows = (
                self.db.query(
                    func.year(Fatura.data_emissao).label("ano"),
                    func.month(Fatura.data_emissao).label("mes"),
                    func.sum(Fatura.valor_final).label("total"),
                )
                .join(OrdemServico, OrdemServico.id == Fatura.ordem_servico_id)
                .filter(
                    OrdemServico.mecanico_id == utilizador_id,
                    cast(Fatura.data_emissao, Date) >= inicio_range,
                )
                .group_by(func.year(Fatura.data_emissao), func.month(Fatura.data_emissao))
                .all()
            )
            faturado_por_mes = {(r.ano, r.mes): float(r.total) for r in rows}

        result = []
        for i in range(meses - 1, -1, -1):  # oldest → newest
            tm = total_months_now - i
            ano = tm // 12
            mes = tm % 12 + 1

            base = float(user.salario_base or 0.0)
            comissao_ganha = 0.0
            if user.perfil == P.MECANICO and user.comissao:
                faturado = faturado_por_mes.get((ano, mes), 0.0)
                comissao_ganha = round(faturado * user.comissao / 100, 2)

            result.append(SalarioHistoricoItem(
                ano=ano,
                mes=mes,
                mes_label=f"{MESES_PT[mes - 1]} {ano}",
                salario_base=base,
                comissao_ganha=comissao_ganha,
                total=round(base + comissao_ganha, 2),
            ))

        return DataResponse(data=result)
