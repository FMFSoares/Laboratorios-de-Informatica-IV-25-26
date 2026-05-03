from __future__ import annotations

# [pendente de integração com BD]
# Dados em memória para a Etapa 3. Substituir por queries reais ao repository
# sem alterar o router nem os schemas.

from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.trotinete import (
    ClienteResumoEmTrotinete,
    TrotineteCreate,
    TrotineteDetalheResponse,
    TrotineteResponse,
)
from app.schemas.utilizador import PerfilUtilizador

# ── Mock data ─────────────────────────────────────────────────────────────────

_MOCK_TROTINETES: list[dict] = [
    {
        "id": 1,
        "cliente_id": 1,
        "loja_id": 1,
        "marca": "Xiaomi",
        "modelo": "Mi Electric Scooter 3",
        "numero_serie": "XM2024ABC123",
        "ano_compra": 2024,
        "cor": "Preto",
        "observacoes_tecnicas": "Bateria substituída em 2025. Controlador original.",
        "data_registo": datetime(2026, 4, 10, 9, 0, tzinfo=timezone.utc),
    },
    {
        "id": 2,
        "cliente_id": 2,
        "loja_id": 1,
        "marca": "Ninebot",
        "modelo": "E45E",
        "numero_serie": "NB2023XYZ456",
        "ano_compra": 2023,
        "cor": "Cinzento",
        "observacoes_tecnicas": None,
        "data_registo": datetime(2026, 4, 12, 11, 30, tzinfo=timezone.utc),
    },
]

_next_id = 3


# ── Helpers ───────────────────────────────────────────────────────────────────


def _find(trotinete_id: int) -> dict | None:
    return next((t for t in _MOCK_TROTINETES if t["id"] == trotinete_id), None)


def _check_loja(trotinete: dict, current_user: CurrentUserResponse) -> None:
    if current_user.perfil == PerfilUtilizador.ADMINISTRADOR:
        return
    if trotinete["loja_id"] != current_user.loja_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "detail": "Acesso a dados de outra loja não permitido.",
                "code": "LOJA_MISMATCH",
            },
        )


def get_por_cliente(cliente_id: int) -> list[dict]:
    """Usado por cliente_service para popular a lista de trotinetes no detalhe."""
    return [t for t in _MOCK_TROTINETES if t["cliente_id"] == cliente_id]


# ── Casos de uso ──────────────────────────────────────────────────────────────


def listar(
    cliente_id: int | None,
    numero_serie: str | None,
    page: int,
    page_size: int,
    current_user: CurrentUserResponse,
) -> PaginatedResponse[TrotineteResponse]:
    itens = list(_MOCK_TROTINETES)

    if current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
        itens = [t for t in itens if t["loja_id"] == current_user.loja_id]

    if cliente_id is not None:
        itens = [t for t in itens if t["cliente_id"] == cliente_id]

    if numero_serie:
        itens = [t for t in itens if t["numero_serie"] == numero_serie]

    total = len(itens)
    pages = max(1, -(-total // page_size))
    start = (page - 1) * page_size

    return PaginatedResponse[TrotineteResponse](
        data=[TrotineteResponse(**{k: v for k, v in t.items() if k != "loja_id"})
              for t in itens[start : start + page_size]],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def criar(
    body: TrotineteCreate,
    current_user: CurrentUserResponse,
) -> DataResponse[TrotineteResponse]:
    global _next_id

    # Import local para evitar dependência circular com cliente_service
    from app.services import cliente_service

    cliente = cliente_service._find(body.cliente_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Cliente não encontrado.", "code": "RESOURCE_NOT_FOUND"},
        )

    # Verifica que o utilizador tem acesso à loja do cliente
    _check_loja({"loja_id": cliente["loja_id"]}, current_user)

    if any(t["numero_serie"] == body.numero_serie for t in _MOCK_TROTINETES):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": "Número de série já registado no sistema.",
                "code": "DUPLICATE_ENTRY",
            },
        )

    nova = {
        "id": _next_id,
        "cliente_id": body.cliente_id,
        "loja_id": cliente["loja_id"],
        "marca": body.marca,
        "modelo": body.modelo,
        "numero_serie": body.numero_serie,
        "ano_compra": body.ano_compra,
        "cor": body.cor,
        "observacoes_tecnicas": body.observacoes_tecnicas,
        "data_registo": datetime.now(timezone.utc),
    }
    _MOCK_TROTINETES.append(nova)
    _next_id += 1

    return DataResponse[TrotineteResponse](
        data=TrotineteResponse(**{k: v for k, v in nova.items() if k != "loja_id"}),
        message="Trotinete registada com sucesso.",
    )


def obter(
    trotinete_id: int,
    current_user: CurrentUserResponse,
) -> DataResponse[TrotineteDetalheResponse]:
    from app.services import cliente_service

    trotinete = _find(trotinete_id)
    if trotinete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Trotinete não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )
    _check_loja(trotinete, current_user)

    cliente = cliente_service._find(trotinete["cliente_id"])
    cliente_resumo = ClienteResumoEmTrotinete(
        id=cliente["id"],
        nome=cliente["nome"],
        telemovel=cliente["telemovel"],
    )

    total_ordens = 0  # [pendente] populado quando OS forem implementadas

    campos = {k: v for k, v in trotinete.items() if k != "loja_id"}
    return DataResponse[TrotineteDetalheResponse](
        data=TrotineteDetalheResponse(
            **campos,
            cliente=cliente_resumo,
            total_ordens=total_ordens,
        ),
    )
