from __future__ import annotations

# [pendente de integração com BD]
# Lojas em memória para a Etapa 3.

from fastapi import HTTPException, status

from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.loja import LojaResponse
from app.schemas.utilizador import PerfilUtilizador
from app.utils.permissions import check_loja_access

# ── Dados canónicos de lojas ──────────────────────────────────────────────────
# Fonte única de verdade enquanto a BD não está integrada.
# fatura_service e stock_service têm cópias parciais que serão removidas
# quando as queries reais substituírem os mocks.

_MOCK_LOJAS: list[dict] = [
    {
        "id": 1,
        "nome": "DLMCare Porto",
        "cidade": "Porto",
        "morada": "Rua de Santa Catarina 100, 4000-447 Porto",
        "telefone": "222000001",
        "email": "porto@dlmcare.pt",
        "ativo": True,
    },
    {
        "id": 2,
        "nome": "DLMCare Lisboa",
        "cidade": "Lisboa",
        "morada": "Av. da Liberdade 100, 1250-096 Lisboa",
        "telefone": "213000001",
        "email": "lisboa@dlmcare.pt",
        "ativo": True,
    },
]


# ── Helpers para outros services ──────────────────────────────────────────────


def _find(loja_id: int) -> dict | None:
    return next((l for l in _MOCK_LOJAS if l["id"] == loja_id), None)


def get_nome(loja_id: int) -> str | None:
    loja = _find(loja_id)
    return loja["nome"] if loja else None


def get_telefone(loja_id: int) -> str | None:
    loja = _find(loja_id)
    return loja["telefone"] if loja else None


# ── Casos de uso ──────────────────────────────────────────────────────────────


def listar(
    page: int,
    page_size: int,
    current_user: CurrentUserResponse,
) -> PaginatedResponse[LojaResponse]:
    itens = list(_MOCK_LOJAS)

    if current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
        itens = [l for l in itens if l["id"] == current_user.loja_id]

    total = len(itens)
    pages = max(1, -(-total // page_size))
    start = (page - 1) * page_size

    return PaginatedResponse[LojaResponse](
        data=[LojaResponse(**l) for l in itens[start : start + page_size]],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def obter(
    loja_id: int,
    current_user: CurrentUserResponse,
) -> DataResponse[LojaResponse]:
    loja = _find(loja_id)
    if loja is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Loja não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )
    check_loja_access(loja_id, current_user)
    return DataResponse[LojaResponse](data=LojaResponse(**loja))
