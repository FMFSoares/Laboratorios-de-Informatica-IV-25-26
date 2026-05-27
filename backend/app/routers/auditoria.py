from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auditoria import TipoEventoAuditoria, AuditoriaItemResponse
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import PaginatedResponse
from app.schemas.utilizador import PerfilUtilizador
from app.auth.dependencies import require_roles
from app.repositories.auditoria_repository import AuditoriaRepository
from app.services.auditoria_service import AuditoriaService

router = APIRouter(prefix="/auditoria", tags=["auditoria"])


def get_auditoria_service(db: Session = Depends(get_db)) -> AuditoriaService:
    return AuditoriaService(AuditoriaRepository(db))


@router.get("/", response_model=PaginatedResponse[AuditoriaItemResponse])
def listar_auditoria(
    evento: TipoEventoAuditoria | None = Query(None),
    utilizador_id: int | None = Query(None),
    loja_id: int | None = Query(None),
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(require_roles(PerfilUtilizador.ADMINISTRADOR)),
    service: AuditoriaService = Depends(get_auditoria_service),
):
    evento_str = evento.value if evento else None
    return service.listar(
        evento=evento_str,
        utilizador_id=utilizador_id,
        loja_id=loja_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        page=page,
        page_size=page_size,
        current_user=current_user,
    )