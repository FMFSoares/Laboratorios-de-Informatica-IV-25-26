from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories.stock_repository import MockStockRepository, StockItem
from app.repositories.loja_repository import MockLojaRepository
from app.repositories.peca_repository import MockPecaRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.stock import (
    StockEntradaRequest,
    StockEntradaResponse,
    StockItemResponse,
    StockTransferenciaRequest,
    StockTransferenciaResponse,
)
from app.schemas.utilizador import PerfilUtilizador
from app.utils.permissions import check_loja_access

_repo = MockStockRepository()
_loja_repo = MockLojaRepository()
_peca_repo = MockPecaRepository()


def _to_item_response(s: StockItem) -> StockItemResponse:
    peca = _peca_repo.get_by_id(s.peca_id)
    loja_nome = _loja_repo.get_nome(s.loja_id) or f"Loja {s.loja_id}"
    return StockItemResponse(
        peca_id=s.peca_id,
        peca_referencia=peca.referencia if peca else "—",
        peca_nome=peca.nome if peca else "—",
        loja_id=s.loja_id,
        loja_nome=loja_nome,
        quantidade=s.quantidade,
        limite_minimo=s.limite_minimo,
        alerta=s.quantidade <= s.limite_minimo,
    )


def consumir_stock(peca_id: int, loja_id: int, quantidade: int) -> None:
    """Reduces stock when a part is applied to an OS. Called by ordem_servico_service."""
    _repo.consumir(peca_id, loja_id, quantidade)


def get_stock_disponivel(peca_id: int, loja_id: int) -> int:
    return _repo.get_disponivel(peca_id, loja_id)


def listar(
    loja_id: int | None,
    apenas_alertas: bool,
    page: int,
    page_size: int,
    current_user: CurrentUserResponse,
) -> PaginatedResponse[StockItemResponse]:
    if current_user.perfil not in (PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA):
        loja_id = current_user.loja_id

    itens, total = _repo.list(loja_id, apenas_alertas, page, page_size)
    pages = max(1, -(-total // page_size))

    return PaginatedResponse[StockItemResponse](
        data=[_to_item_response(s) for s in itens],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def atualizar_minimo(
    peca_id: int,
    loja_id: int,
    limite_minimo: int,
    current_user: CurrentUserResponse,
) -> DataResponse[StockItemResponse]:
    check_loja_access(loja_id, current_user)

    if not _loja_repo.exists(loja_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Loja não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )
    if _peca_repo.get_by_id(peca_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Peça não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )

    item = _repo.atualizar_minimo(peca_id, loja_id, limite_minimo)
    return DataResponse[StockItemResponse](
        data=_to_item_response(item),
        message="Limite mínimo atualizado.",
    )


def entrada(
    body: StockEntradaRequest,
    current_user: CurrentUserResponse,
) -> DataResponse[StockEntradaResponse]:
    check_loja_access(body.loja_id, current_user)

    if not _loja_repo.exists(body.loja_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Loja não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )

    peca = _peca_repo.get_by_id(body.peca_id)
    if peca is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Peça não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )

    item = _repo.get_or_create(body.peca_id, body.loja_id)
    quantidade_anterior = item.quantidade
    item = _repo.adicionar(body.peca_id, body.loja_id, body.quantidade)

    return DataResponse[StockEntradaResponse](
        data=StockEntradaResponse(
            peca_id=body.peca_id,
            peca_nome=peca.nome,
            loja_id=body.loja_id,
            quantidade_anterior=quantidade_anterior,
            quantidade_adicionada=body.quantidade,
            quantidade_atual=item.quantidade,
            alerta=item.quantidade <= item.limite_minimo,
        ),
        message="Entrada de stock registada.",
    )


def transferencia(
    body: StockTransferenciaRequest,
    current_user: CurrentUserResponse,
) -> DataResponse[StockTransferenciaResponse]:
    check_loja_access(body.loja_origem_id, current_user)

    for loja_id in (body.loja_origem_id, body.loja_destino_id):
        if not _loja_repo.exists(loja_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": f"Loja {loja_id} não encontrada.", "code": "RESOURCE_NOT_FOUND"},
            )

    peca = _peca_repo.get_by_id(body.peca_id)
    if peca is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Peça não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )

    origem, destino = _repo.transferir(body.peca_id, body.loja_origem_id, body.loja_destino_id, body.quantidade)

    return DataResponse[StockTransferenciaResponse](
        data=StockTransferenciaResponse(
            peca_id=body.peca_id,
            peca_nome=peca.nome,
            loja_origem_id=body.loja_origem_id,
            loja_destino_id=body.loja_destino_id,
            quantidade_transferida=body.quantidade,
            stock_origem_apos=origem.quantidade,
            stock_destino_apos=destino.quantidade,
        ),
        message="Transferência de stock concluída.",
    )
