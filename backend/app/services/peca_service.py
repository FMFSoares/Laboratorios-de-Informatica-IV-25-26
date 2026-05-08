from __future__ import annotations

# [pendente de integração com BD]
# Catálogo de peças em memória para a Etapa 3.
# preco_custo é armazenado internamente mas nunca exposto em respostas públicas.

from fastapi import HTTPException, status

from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.peca import CategoriaPeca, PecaCreate, PecaDetalheResponse, PecaResponse

# ── Mock data ─────────────────────────────────────────────────────────────────

_MOCK_PECAS: list[dict] = [
    {
        "id": 1,
        "referencia": "PEC-BAT-001",
        "nome": "Bateria 36V 7.5Ah Xiaomi",
        "categoria": CategoriaPeca.BATERIA,
        "descricao": "Bateria de substituição compatível com Xiaomi M365 e Pro.",
        "unidade": "unidade",
        "preco_custo": 42.00,
        "preco_venda": 89.90,
        "ativo": True,
    },
    {
        "id": 2,
        "referencia": "PEC-PNE-001",
        "nome": "Pneu Traseiro 8.5x2 Xiaomi",
        "categoria": CategoriaPeca.PNEU,
        "descricao": "Pneu anti-furo para trotinetes Xiaomi e compatíveis.",
        "unidade": "unidade",
        "preco_custo": 8.50,
        "preco_venda": 18.90,
        "ativo": True,
    },
    {
        "id": 3,
        "referencia": "PEC-TRA-001",
        "nome": "Pastilhas de Travão Ninebot",
        "categoria": CategoriaPeca.TRAVAO,
        "descricao": "Kit de pastilhas para travões de disco Ninebot.",
        "unidade": "par",
        "preco_custo": 5.00,
        "preco_venda": 12.50,
        "ativo": True,
    },
    {
        "id": 4,
        "referencia": "PEC-MOT-001",
        "nome": "Motor Hub 250W",
        "categoria": CategoriaPeca.MOTOR,
        "descricao": "Motor de substituição 250W compatível com múltiplas marcas.",
        "unidade": "unidade",
        "preco_custo": 95.00,
        "preco_venda": 195.00,
        "ativo": True,
    },
]

_next_id = 5


# ── Helpers internos ──────────────────────────────────────────────────────────


def _find(peca_id: int) -> dict | None:
    return next((p for p in _MOCK_PECAS if p["id"] == peca_id), None)


def get_peca_interna(peca_id: int) -> dict | None:
    """Devolve o dict completo da peça (inclui preco_custo) para uso interno por outros services."""
    return _find(peca_id)


def _to_response(peca: dict) -> PecaResponse:
    # preco_custo é ignorado pelo schema PecaResponse (extra='ignore' por defeito no Pydantic v2)
    return PecaResponse(**peca)


# ── Casos de uso ──────────────────────────────────────────────────────────────


def listar(
    query: str | None,
    categoria: CategoriaPeca | None,
    page: int,
    page_size: int,
) -> PaginatedResponse[PecaResponse]:
    itens = [p for p in _MOCK_PECAS if p["ativo"]]

    if categoria:
        itens = [p for p in itens if p["categoria"] == categoria]

    if query:
        q = query.lower()
        itens = [
            p for p in itens
            if q in p["nome"].lower() or q in p["referencia"].lower()
        ]

    total = len(itens)
    pages = max(1, -(-total // page_size))
    start = (page - 1) * page_size

    return PaginatedResponse[PecaResponse](
        data=[_to_response(p) for p in itens[start : start + page_size]],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def obter(peca_id: int) -> DataResponse[PecaDetalheResponse]:
    peca = _find(peca_id)
    if peca is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Peça não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )
    return DataResponse[PecaDetalheResponse](
        data=PecaDetalheResponse(**peca),
    )


def criar(body: PecaCreate) -> DataResponse[PecaResponse]:
    global _next_id

    if any(p["referencia"] == body.referencia for p in _MOCK_PECAS):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Referência já registada no sistema.", "code": "DUPLICATE_ENTRY"},
        )

    nova = {
        "id": _next_id,
        "referencia": body.referencia,
        "nome": body.nome,
        "categoria": body.categoria,
        "descricao": body.descricao,
        "unidade": body.unidade,
        "preco_custo": body.preco_custo,
        "preco_venda": body.preco_venda,
        "ativo": True,
    }
    _MOCK_PECAS.append(nova)
    _next_id += 1

    return DataResponse[PecaResponse](
        data=_to_response(nova),
        message="Peça criada com sucesso.",
    )
