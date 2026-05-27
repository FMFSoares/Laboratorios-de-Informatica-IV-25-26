from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.schemas.auth import CurrentUserResponse
from app.schemas.notificacao import NotificacaoResponse
from app.schemas.common import PaginatedResponse
from app.services.notificacao_service import NotificacaoService

router = APIRouter(prefix="/notificacoes", tags=["notificacoes"])


def get_service(db: Session = Depends(get_db)) -> NotificacaoService:
    return NotificacaoService(db)


@router.get("/count")
def count_nao_lidas(
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: NotificacaoService = Depends(get_service),
):
    return {"nao_lidas": service.count_nao_lidas(current_user)}


@router.get("/", response_model=PaginatedResponse[NotificacaoResponse])
def listar(
    apenas_nao_lidas: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: NotificacaoService = Depends(get_service),
):
    return service.listar(page, page_size, apenas_nao_lidas, current_user)


@router.post("/ler-todas", status_code=204)
def marcar_todas_lidas(
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: NotificacaoService = Depends(get_service),
):
    service.marcar_todas_lidas(current_user)


@router.delete("/", status_code=204)
def apagar_todas(
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: NotificacaoService = Depends(get_service),
):
    service.apagar_todas(current_user)


@router.delete("/{notificacao_id}", status_code=204)
def apagar_uma(
    notificacao_id: int,
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: NotificacaoService = Depends(get_service),
):
    service.apagar_uma(notificacao_id, current_user)


@router.post("/{notificacao_id}/ler", status_code=204)
def marcar_lida(
    notificacao_id: int,
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: NotificacaoService = Depends(get_service),
):
    service.marcar_lida(notificacao_id, current_user)
