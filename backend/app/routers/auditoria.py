from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import require_roles
from app.schemas.auth import CurrentUserResponse
from app.schemas.auditoria import AuditoriaItemResponse, TipoEventoAuditoria
from app.schemas.common import PaginatedResponse
from app.schemas.utilizador import PerfilUtilizador
from app.services import auditoria_service

router = APIRouter(prefix="/auditoria", tags=["auditoria"])

_gestores = require_roles(
    PerfilUtilizador.ADMINISTRADOR,
    PerfilUtilizador.GERENTE_LOJA,
)


@router.get(
    "",
    response_model=PaginatedResponse[AuditoriaItemResponse],
    summary="Listar registos de auditoria",
)
def listar(
    evento: TipoEventoAuditoria | None = Query(None, description="Filtrar por tipo de evento."),
    utilizador_id: int | None = Query(None, description="Filtrar por utilizador."),
    loja_id: int | None = Query(None, description="Filtrar por loja (ADMINISTRADOR apenas)."),
    data_inicio: date | None = Query(None, description="Data a partir de (ISO 8601)."),
    data_fim: date | None = Query(None, description="Data até (ISO 8601)."),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(_gestores),
) -> PaginatedResponse[AuditoriaItemResponse]:
    return auditoria_service.listar(
        evento.value if evento else None,
        utilizador_id,
        loja_id,
        data_inicio,
        data_fim,
        page,
        page_size,
        current_user,
    )
