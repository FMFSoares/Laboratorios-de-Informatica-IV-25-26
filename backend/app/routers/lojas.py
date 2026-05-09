from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_user
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.loja import LojaResponse
from app.services import loja_service

router = APIRouter(prefix="/lojas", tags=["lojas"])


@router.get(
    "",
    response_model=PaginatedResponse[LojaResponse],
    summary="Listar lojas",
)
def listar(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUserResponse = Depends(get_current_user),
) -> PaginatedResponse[LojaResponse]:
    return loja_service.listar(page, page_size, current_user)


@router.get(
    "/{loja_id}",
    response_model=DataResponse[LojaResponse],
    summary="Detalhe de loja",
    responses={
        403: {"description": "LOJA_MISMATCH"},
        404: {"description": "Loja não encontrada"},
    },
)
def obter(
    loja_id: int,
    current_user: CurrentUserResponse = Depends(get_current_user),
) -> DataResponse[LojaResponse]:
    return loja_service.obter(loja_id, current_user)
