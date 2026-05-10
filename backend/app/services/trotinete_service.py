from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories.trotinete_repository import MockTrotineteRepository, Trotinete
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.trotinete import (
    ClienteResumoEmTrotinete,
    TrotineteCreate,
    TrotineteDetalheResponse,
    TrotineteResponse,
)
from app.schemas.utilizador import PerfilUtilizador
from app.utils.permissions import check_loja_access

_repo = MockTrotineteRepository()


def _to_response(t: Trotinete) -> TrotineteResponse:
    data = {k: v for k, v in t.__dict__.items() if k != "loja_id"}
    return TrotineteResponse(**data)


def _find(trotinete_id: int) -> Trotinete | None:
    """Cross-service lookup used by fatura_service and ordem_servico_service."""
    return _repo.get_by_id(trotinete_id)


def get_por_cliente(cliente_id: int) -> list[Trotinete]:
    """Used by cliente_service to populate the trotinetes list on client detail."""
    return _repo.list_by_cliente(cliente_id)


def listar(
    cliente_id: int | None,
    numero_serie: str | None,
    page: int,
    page_size: int,
    current_user: CurrentUserResponse,
) -> PaginatedResponse[TrotineteResponse]:
    loja_id = None if current_user.perfil == PerfilUtilizador.ADMINISTRADOR else current_user.loja_id
    itens, total = _repo.list(loja_id, cliente_id, numero_serie, page, page_size)
    pages = max(1, -(-total // page_size))

    return PaginatedResponse[TrotineteResponse](
        data=[_to_response(t) for t in itens],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def criar(
    body: TrotineteCreate,
    current_user: CurrentUserResponse,
) -> DataResponse[TrotineteResponse]:
    from app.services import cliente_service

    cliente = cliente_service._find(body.cliente_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Cliente não encontrado.", "code": "RESOURCE_NOT_FOUND"},
        )

    check_loja_access(cliente.loja_id, current_user)

    if _repo.exists_numero_serie(body.numero_serie):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Número de série já registado no sistema.", "code": "DUPLICATE_ENTRY"},
        )

    nova = _repo.create(
        cliente_id=body.cliente_id,
        loja_id=cliente.loja_id,
        marca=body.marca,
        modelo=body.modelo,
        numero_serie=body.numero_serie,
        ano_compra=body.ano_compra,
        cor=body.cor,
        observacoes_tecnicas=body.observacoes_tecnicas,
    )

    return DataResponse[TrotineteResponse](
        data=_to_response(nova),
        message="Trotinete registada com sucesso.",
    )


def obter(
    trotinete_id: int,
    current_user: CurrentUserResponse,
) -> DataResponse[TrotineteDetalheResponse]:
    from app.services import cliente_service

    trotinete = _repo.get_by_id(trotinete_id)
    if trotinete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Trotinete não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )
    check_loja_access(trotinete.loja_id, current_user)

    cliente = cliente_service._find(trotinete.cliente_id)
    cliente_resumo = ClienteResumoEmTrotinete(
        id=cliente.id,
        nome=cliente.nome,
        telemovel=cliente.telemovel,
    )

    total_ordens = _repo.count_by_trotinete(trotinete_id)
    data = {k: v for k, v in trotinete.__dict__.items() if k != "loja_id"}

    return DataResponse[TrotineteDetalheResponse](
        data=TrotineteDetalheResponse(**data, cliente=cliente_resumo, total_ordens=total_ordens),
    )
