from __future__ import annotations

import math
from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.schemas.auth import AuthUserInfo
from app.schemas.cliente import (
    ClienteCreate,
    ClienteDetalheResponse,
    ClienteHistoricoItem,
    ClienteResponse,
    TrotineteResumoEmCliente,
)
from app.schemas.common import PaginatedResponse
from app.schemas.utilizador import PerfilUtilizador

# ── Mock store ────────────────────────────────────────────────────────────────

_clientes: list[dict] = [
    {
        "id": 1,
        "nome": "João Silva",
        "nif": "123456789",
        "telemovel": "912345678",
        "email": "joao.silva@email.com",
        "morada": "Rua das Flores 10, Lisboa",
        "consentimento_rgpd": True,
        "data_registo": datetime(2026, 1, 10, 9, 0, 0, tzinfo=timezone.utc),
        "loja_id": 2,
        "trotinetes": [
            {"id": 1, "marca": "Xiaomi", "modelo": "Mi Electric Scooter 3", "numero_serie": "XM2024ABC123"}
        ],
    },
    {
        "id": 2,
        "nome": "Maria Santos",
        "nif": "987654321",
        "telemovel": "961234567",
        "email": "maria.santos@email.com",
        "morada": "Av. da Liberdade 50, Lisboa",
        "consentimento_rgpd": True,
        "data_registo": datetime(2026, 2, 5, 14, 0, 0, tzinfo=timezone.utc),
        "loja_id": 2,
        "trotinetes": [],
    },
    {
        "id": 3,
        "nome": "Carlos Ferreira",
        "nif": "111222333",
        "telemovel": "931122334",
        "email": None,
        "morada": "Rua do Porto 7, Porto",
        "consentimento_rgpd": True,
        "data_registo": datetime(2026, 3, 1, 11, 0, 0, tzinfo=timezone.utc),
        "loja_id": 1,
        "trotinetes": [],
    },
]

_next_id = 4

_nifs: set[str] = {c["nif"] for c in _clientes}

# ── Mock histórico (estático até OS estar implementado) ───────────────────────

_historico_mock: dict[int, list[dict]] = {
    1: [
        {
            "id": 10,
            "trotinete_numero_serie": "XM2024ABC123",
            "descricao": "Diagnóstico geral + substituição de pneu",
            "estado": "FATURADA",
            "data_entrada": datetime(2026, 3, 15, 9, 0, 0, tzinfo=timezone.utc),
            "data_conclusao": datetime(2026, 3, 16, 17, 0, 0, tzinfo=timezone.utc),
            "valor_final": 45.50,
        }
    ]
}


# ── Helpers ───────────────────────────────────────────────────────────────────


def _check_loja_access(user: AuthUserInfo, loja_id: int) -> None:
    if user.perfil != PerfilUtilizador.ADMINISTRADOR and user.loja_id != loja_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não tem acesso a dados de outra loja.",
            headers={"X-Error-Code": "LOJA_MISMATCH"},
        )


def _effective_loja_id(user: AuthUserInfo) -> int | None:
    """None significa sem filtro (ADMINISTRADOR). Outros sempre ficam limitados à sua loja."""
    if user.perfil == PerfilUtilizador.ADMINISTRADOR:
        return None
    return user.loja_id


def _to_response(c: dict) -> ClienteResponse:
    return ClienteResponse(
        id=c["id"],
        nome=c["nome"],
        nif=c["nif"],
        telemovel=c["telemovel"],
        email=c["email"],
        morada=c["morada"],
        consentimento_rgpd=c["consentimento_rgpd"],
        data_registo=c["data_registo"],
        loja_id=c["loja_id"],
    )


def _to_detalhe(c: dict) -> ClienteDetalheResponse:
    return ClienteDetalheResponse(
        id=c["id"],
        nome=c["nome"],
        nif=c["nif"],
        telemovel=c["telemovel"],
        email=c["email"],
        morada=c["morada"],
        consentimento_rgpd=c["consentimento_rgpd"],
        data_registo=c["data_registo"],
        loja_id=c["loja_id"],
        trotinetes=[TrotineteResumoEmCliente(**t) for t in c["trotinetes"]],
    )


def _paginate(items: list, page: int, page_size: int) -> tuple[list, int, int]:
    """Returns (page_items, total, pages)."""
    total = len(items)
    pages = max(1, math.ceil(total / page_size)) if total else 1
    start = (page - 1) * page_size
    return items[start : start + page_size], total, pages


# ── Service functions ─────────────────────────────────────────────────────────


def list_clientes(
    query: str | None,
    page: int,
    page_size: int,
    current_user: AuthUserInfo,
) -> PaginatedResponse[ClienteResponse]:
    loja_filter = _effective_loja_id(current_user)

    results = [
        c for c in _clientes
        if (loja_filter is None or c["loja_id"] == loja_filter)
        and (
            query is None
            or c["nif"] == query
            or c["telemovel"] == query
        )
    ]

    page_items, total, pages = _paginate(results, page, page_size)

    return PaginatedResponse[ClienteResponse](
        data=[_to_response(c) for c in page_items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def create_cliente(
    data: ClienteCreate,
    current_user: AuthUserInfo,
) -> ClienteResponse:
    global _next_id

    if data.nif in _nifs:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um cliente com este NIF.",
            headers={"X-Error-Code": "DUPLICATE_ENTRY"},
        )

    loja_id = current_user.loja_id if current_user.loja_id is not None else 1

    novo = {
        "id": _next_id,
        "nome": data.nome,
        "nif": data.nif,
        "telemovel": data.telemovel,
        "email": str(data.email) if data.email else None,
        "morada": data.morada,
        "consentimento_rgpd": data.consentimento_rgpd,
        "data_registo": datetime.now(timezone.utc),
        "loja_id": loja_id,
        "trotinetes": [],
    }

    _clientes.append(novo)
    _nifs.add(data.nif)
    _next_id += 1

    return _to_response(novo)


def get_cliente(
    cliente_id: int,
    current_user: AuthUserInfo,
) -> ClienteDetalheResponse:
    cliente = next((c for c in _clientes if c["id"] == cliente_id), None)

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado.",
            headers={"X-Error-Code": "RESOURCE_NOT_FOUND"},
        )

    _check_loja_access(current_user, cliente["loja_id"])
    return _to_detalhe(cliente)


def get_historico(
    cliente_id: int,
    page: int,
    page_size: int,
    current_user: AuthUserInfo,
) -> PaginatedResponse[ClienteHistoricoItem]:
    cliente = next((c for c in _clientes if c["id"] == cliente_id), None)

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado.",
            headers={"X-Error-Code": "RESOURCE_NOT_FOUND"},
        )

    _check_loja_access(current_user, cliente["loja_id"])

    historico = _historico_mock.get(cliente_id, [])
    page_items, total, pages = _paginate(historico, page, page_size)

    return PaginatedResponse[ClienteHistoricoItem](
        data=[ClienteHistoricoItem(**h) for h in page_items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
