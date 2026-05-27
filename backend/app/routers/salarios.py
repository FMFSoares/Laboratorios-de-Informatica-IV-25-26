from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse
from app.schemas.salario import SalarioHistoricoItem, SalarioUtilizador
from app.schemas.utilizador import PerfilUtilizador
from app.services.salario_service import SalarioService

router = APIRouter(prefix="/salarios", tags=["salários"])

_gestores = require_roles(PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA)


def get_salario_service(db: Session = Depends(get_db)) -> SalarioService:
    return SalarioService(db)


@router.get(
    "",
    response_model=DataResponse[list[SalarioUtilizador]],
    summary="Calcular salários do mês (Administrador e Gerente de Loja)",
)
def calcular(
    ano: int = Query(..., ge=2000, le=2100, description="Ano do período."),
    mes: int = Query(..., ge=1, le=12, description="Mês do período (1-12)."),
    current_user: CurrentUserResponse = Depends(_gestores),
    service: SalarioService = Depends(get_salario_service),
) -> DataResponse[list[SalarioUtilizador]]:
    return service.calcular(ano, mes, current_user)


@router.get(
    "/{utilizador_id}/historico",
    response_model=DataResponse[list[SalarioHistoricoItem]],
    summary="Histórico de salários de um utilizador (Administrador)",
)
def historico(
    utilizador_id: int,
    meses: int = Query(12, ge=1, le=36, description="Número de meses a retornar."),
    _: CurrentUserResponse = Depends(require_roles(PerfilUtilizador.ADMINISTRADOR)),
    service: SalarioService = Depends(get_salario_service),
) -> DataResponse[list[SalarioHistoricoItem]]:
    return service.calcular_historico(utilizador_id, meses)
