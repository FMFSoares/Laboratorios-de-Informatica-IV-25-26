from __future__ import annotations

# [pendente de integração com BD]
# Dados em memória para a Etapa 3. Substituir _MOCK_CLIENTES por queries reais
# ao repository sem alterar o router nem os schemas.

from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.schemas.auth import CurrentUserResponse
from app.schemas.cliente import (
    ClienteCreate,
    ClienteDetalheResponse,
    ClienteHistoricoItem,
    ClienteResponse,
)
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.utilizador import PerfilUtilizador

# ── Mock data ─────────────────────────────────────────────────────────────────

_MOCK_CLIENTES: list[dict] = [
    {
        "id": 1,
        "nome": "João Silva",
        "nif": "123456789",
        "telemovel": "912345678",
        "email": "joao.silva@email.com",
        "morada": "Rua das Flores 10, Porto",
        "consentimento_rgpd": True,
        "data_registo": datetime(2026, 4, 1, 10, 0, tzinfo=timezone.utc),
        "loja_id": 1,
    },
    {
        "id": 2,
        "nome": "Maria Santos",
        "nif": "987654321",
        "telemovel": "961234567",
        "email": "maria.santos@email.com",
        "morada": "Av. da Liberdade 5, Porto",
        "consentimento_rgpd": True,
        "data_registo": datetime(2026, 4, 5, 14, 30, tzinfo=timezone.utc),
        "loja_id": 1,
    },
]

_next_id = 3


# ── Helpers ───────────────────────────────────────────────────────────────────


def _find(cliente_id: int) -> dict | None:
    return next((c for c in _MOCK_CLIENTES if c["id"] == cliente_id), None)


def _check_loja(cliente: dict, current_user: CurrentUserResponse) -> None:
    if current_user.perfil == PerfilUtilizador.ADMINISTRADOR:
        return
    if cliente["loja_id"] != current_user.loja_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "detail": "Acesso a dados de outra loja não permitido.",
                "code": "LOJA_MISMATCH",
            },
        )


# ── Casos de uso ──────────────────────────────────────────────────────────────


def listar(
    query: str | None,
    page: int,
    page_size: int,
    current_user: CurrentUserResponse,
) -> PaginatedResponse[ClienteResponse]:
    itens = list(_MOCK_CLIENTES)

    if current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
        itens = [c for c in itens if c["loja_id"] == current_user.loja_id]

    if query:
        itens = [c for c in itens if c["nif"] == query or c["telemovel"] == query]

    total = len(itens)
    pages = max(1, -(-total // page_size))
    start = (page - 1) * page_size

    return PaginatedResponse[ClienteResponse](
        data=[ClienteResponse(**c) for c in itens[start : start + page_size]],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def criar(
    body: ClienteCreate,
    current_user: CurrentUserResponse,
) -> DataResponse[ClienteResponse]:
    global _next_id

    if any(c["nif"] == body.nif for c in _MOCK_CLIENTES):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "NIF já registado no sistema.", "code": "DUPLICATE_ENTRY"},
        )

    # Para ADMINISTRADOR sem loja_id, usa a loja 1 como fallback no mock
    loja_id = current_user.loja_id or 1

    novo = {
        "id": _next_id,
        "nome": body.nome,
        "nif": body.nif,
        "telemovel": body.telemovel,
        "email": str(body.email) if body.email else None,
        "morada": body.morada,
        "consentimento_rgpd": body.consentimento_rgpd,
        "data_registo": datetime.now(timezone.utc),
        "loja_id": loja_id,
    }
    _MOCK_CLIENTES.append(novo)
    _next_id += 1

    return DataResponse[ClienteResponse](
        data=ClienteResponse(**novo),
        message="Cliente registado com sucesso.",
    )


def obter(
    cliente_id: int,
    current_user: CurrentUserResponse,
) -> DataResponse[ClienteDetalheResponse]:
    cliente = _find(cliente_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Cliente não encontrado.", "code": "RESOURCE_NOT_FOUND"},
        )
    _check_loja(cliente, current_user)

    # Import local para evitar dependência circular com trotinete_service
    from app.services import trotinete_service
    from app.schemas.cliente import TrotineteResumoEmCliente

    trotinetes = [
        TrotineteResumoEmCliente(
            id=t["id"], marca=t["marca"], modelo=t["modelo"], numero_serie=t["numero_serie"]
        )
        for t in trotinete_service.get_por_cliente(cliente["id"])
    ]

    return DataResponse[ClienteDetalheResponse](
        data=ClienteDetalheResponse(**cliente, trotinetes=trotinetes),
    )


def historico(
    cliente_id: int,
    page: int,
    page_size: int,
    current_user: CurrentUserResponse,
) -> PaginatedResponse[ClienteHistoricoItem]:
    cliente = _find(cliente_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Cliente não encontrado.", "code": "RESOURCE_NOT_FOUND"},
        )
    _check_loja(cliente, current_user)

    # [pendente de integração com BD] — populado quando OS forem implementadas
    return PaginatedResponse[ClienteHistoricoItem](
        data=[],
        total=0,
        page=page,
        page_size=page_size,
        pages=1,
    )
