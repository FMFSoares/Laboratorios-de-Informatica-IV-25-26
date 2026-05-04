from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse
from app.schemas.dashboard import DashboardResponse
from app.schemas.utilizador import PerfilUtilizador
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

_gestores = require_roles(
    PerfilUtilizador.ADMINISTRADOR,
    PerfilUtilizador.GERENTE_LOJA,
)


@router.get(
    "",
    response_model=DataResponse[DashboardResponse],
    summary="Métricas agregadas do sistema",
)
def obter(
    loja_id: int | None = Query(None, description="Filtrar por loja (ADMINISTRADOR apenas)."),
    data_inicio: date | None = Query(None, description="Início do período (ISO 8601)."),
    data_fim: date | None = Query(None, description="Fim do período (ISO 8601)."),
    current_user: CurrentUserResponse = Depends(_gestores),
) -> DataResponse[DashboardResponse]:
    return dashboard_service.obter(loja_id, data_inicio, data_fim, current_user)
