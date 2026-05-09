from __future__ import annotations

# [pendente de integração com BD]
# Stock por loja em memória para a Etapa 3.
# Movimentos de auditoria marcados como [pendente] — serão emitidos quando
# auditoria_service estiver implementado.

from fastapi import HTTPException, status

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

# ── Mock data ─────────────────────────────────────────────────────────────────

# Lojas conhecidas no mock (loja_id → nome)
_MOCK_LOJAS: dict[int, str] = {
    1: "DLMCare Porto",
    2: "DLMCare Lisboa",
}

# Stock: lista de dicts {peca_id, loja_id, quantidade, limite_minimo}
_MOCK_STOCK: list[dict] = [
    {"peca_id": 1, "loja_id": 1, "quantidade": 3,  "limite_minimo": 5},
    {"peca_id": 2, "loja_id": 1, "quantidade": 12, "limite_minimo": 3},
    {"peca_id": 3, "loja_id": 1, "quantidade": 8,  "limite_minimo": 2},
    {"peca_id": 4, "loja_id": 1, "quantidade": 2,  "limite_minimo": 2},
    {"peca_id": 1, "loja_id": 2, "quantidade": 0,  "limite_minimo": 3},
    {"peca_id": 2, "loja_id": 2, "quantidade": 5,  "limite_minimo": 2},
]


# ── Helpers internos ──────────────────────────────────────────────────────────


def _find_stock(peca_id: int, loja_id: int) -> dict | None:
    return next(
        (s for s in _MOCK_STOCK if s["peca_id"] == peca_id and s["loja_id"] == loja_id),
        None,
    )


def _get_or_create_stock(peca_id: int, loja_id: int) -> dict:
    item = _find_stock(peca_id, loja_id)
    if item is None:
        item = {"peca_id": peca_id, "loja_id": loja_id, "quantidade": 0, "limite_minimo": 2}
        _MOCK_STOCK.append(item)
    return item


def _to_item_response(s: dict) -> StockItemResponse:
    from app.services.peca_service import get_peca_interna
    peca = get_peca_interna(s["peca_id"])
    return StockItemResponse(
        peca_id=s["peca_id"],
        peca_referencia=peca["referencia"] if peca else "—",
        peca_nome=peca["nome"] if peca else "—",
        loja_id=s["loja_id"],
        loja_nome=_MOCK_LOJAS.get(s["loja_id"], f"Loja {s['loja_id']}"),
        quantidade=s["quantidade"],
        limite_minimo=s["limite_minimo"],
        alerta=s["quantidade"] <= s["limite_minimo"],
    )



def get_stock_disponivel(peca_id: int, loja_id: int) -> int:
    """Helper para outros services verificarem stock antes de consumir."""
    item = _find_stock(peca_id, loja_id)
    return item["quantidade"] if item else 0


def consumir_stock(peca_id: int, loja_id: int, quantidade: int) -> None:
    """Reduz o stock quando uma peça é aplicada numa OS. Chamado por ordem_servico_service."""
    item = _find_stock(peca_id, loja_id)
    if item is None or item["quantidade"] < quantidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": "Stock insuficiente.", "code": "INSUFFICIENT_STOCK"},
        )
    item["quantidade"] -= quantidade


# ── Casos de uso ──────────────────────────────────────────────────────────────


def listar(
    loja_id: int | None,
    apenas_alertas: bool,
    page: int,
    page_size: int,
    current_user: CurrentUserResponse,
) -> PaginatedResponse[StockItemResponse]:
    # Determina loja_id efectiva
    if current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
        loja_id = current_user.loja_id

    itens = list(_MOCK_STOCK)

    if loja_id is not None:
        itens = [s for s in itens if s["loja_id"] == loja_id]

    if apenas_alertas:
        itens = [s for s in itens if s["quantidade"] <= s["limite_minimo"]]

    total = len(itens)
    pages = max(1, -(-total // page_size))
    start = (page - 1) * page_size

    return PaginatedResponse[StockItemResponse](
        data=[_to_item_response(s) for s in itens[start : start + page_size]],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def entrada(
    body: StockEntradaRequest,
    current_user: CurrentUserResponse,
) -> DataResponse[StockEntradaResponse]:
    from app.services.peca_service import get_peca_interna

    check_loja_access(body.loja_id, current_user)

    if body.loja_id not in _MOCK_LOJAS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Loja não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )

    peca = get_peca_interna(body.peca_id)
    if peca is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Peça não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )

    item = _get_or_create_stock(body.peca_id, body.loja_id)
    quantidade_anterior = item["quantidade"]
    item["quantidade"] += body.quantidade

    # [pendente] auditoria STOCK_ENTRADA

    return DataResponse[StockEntradaResponse](
        data=StockEntradaResponse(
            peca_id=body.peca_id,
            peca_nome=peca["nome"],
            loja_id=body.loja_id,
            quantidade_anterior=quantidade_anterior,
            quantidade_adicionada=body.quantidade,
            quantidade_atual=item["quantidade"],
            alerta=item["quantidade"] <= item["limite_minimo"],
        ),
        message="Entrada de stock registada.",
    )


def transferencia(
    body: StockTransferenciaRequest,
    current_user: CurrentUserResponse,
) -> DataResponse[StockTransferenciaResponse]:
    from app.services.peca_service import get_peca_interna

    # Não-ADMIN só pode transferir a partir da sua própria loja
    check_loja_access(body.loja_origem_id, current_user)

    for loja_id in (body.loja_origem_id, body.loja_destino_id):
        if loja_id not in _MOCK_LOJAS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": f"Loja {loja_id} não encontrada.", "code": "RESOURCE_NOT_FOUND"},
            )

    peca = get_peca_interna(body.peca_id)
    if peca is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Peça não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )

    origem = _get_or_create_stock(body.peca_id, body.loja_origem_id)
    if origem["quantidade"] < body.quantidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": f"Stock insuficiente na loja de origem (disponível: {origem['quantidade']}).",
                "code": "INSUFFICIENT_STOCK",
            },
        )

    destino = _get_or_create_stock(body.peca_id, body.loja_destino_id)
    origem["quantidade"] -= body.quantidade
    destino["quantidade"] += body.quantidade

    # [pendente] auditoria STOCK_TRANSFERENCIA

    return DataResponse[StockTransferenciaResponse](
        data=StockTransferenciaResponse(
            peca_id=body.peca_id,
            peca_nome=peca["nome"],
            loja_origem_id=body.loja_origem_id,
            loja_destino_id=body.loja_destino_id,
            quantidade_transferida=body.quantidade,
            stock_origem_apos=origem["quantidade"],
            stock_destino_apos=destino["quantidade"],
        ),
        message="Transferência de stock concluída.",
    )
