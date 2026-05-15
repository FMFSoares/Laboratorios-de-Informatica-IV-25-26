from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auditoria import TipoEventoAuditoria, AuditoriaItemResponse
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import PaginatedResponse
from app.schemas.utilizador import PerfilUtilizador
from app.auth.dependencies import require_roles, get_current_user
from app.services import auditoria_service

router = APIRouter(prefix="/auditoria", tags=["auditoria"])

@router.get("/", response_model=PaginatedResponse[AuditoriaItemResponse])
def listar_auditoria(
    evento: TipoEventoAuditoria | None = Query(None),
    utilizador_id: int | None = Query(None),
    loja_id: int | None = Query(None),
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(require_roles(PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA)),
    db: Session = Depends(get_db)
):
    evento_str = evento.value if evento else None
    return auditoria_service.listar(
        db=db,
        evento=evento_str,
        utilizador_id=utilizador_id,
        loja_id=loja_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        page=page,
        page_size=page_size,
        current_user=current_user
    )