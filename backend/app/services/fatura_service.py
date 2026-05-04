from __future__ import annotations

# [pendente de integração com BD]
# Faturas em memória para a Etapa 3.

from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.fatura import (
    EstadoFatura,
    FaturaClienteInfo,
    FaturaLojaInfo,
    FaturaPecaAplicada,
    FaturaResumo,
    FaturaResponse,
    FaturaServicoInfo,
    FaturaTrotineteInfo,
)
from app.schemas.utilizador import PerfilUtilizador as P

# ── Dados de lojas (morada e telefone para imprimir na fatura) ────────────────

_MOCK_LOJAS_INFO: dict[int, dict] = {
    1: {"nome": "DLMCare Porto",   "morada": "Rua de Santa Catarina 100, 4000-447 Porto",  "telefone": "222000001"},
    2: {"nome": "DLMCare Lisboa",  "morada": "Av. da Liberdade 100, 1250-096 Lisboa",       "telefone": "213000001"},
}

# ── Mock data ─────────────────────────────────────────────────────────────────

_MOCK_FATURAS: list[dict] = []
_next_id = 1


# ── Helpers internos ──────────────────────────────────────────────────────────


def _find(fatura_id: int) -> dict | None:
    return next((f for f in _MOCK_FATURAS if f["id"] == fatura_id), None)


def _check_loja(fatura: dict, current_user: CurrentUserResponse) -> None:
    if current_user.perfil == P.ADMINISTRADOR:
        return
    if fatura["loja_id"] != current_user.loja_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"detail": "Acesso a dados de outra loja não permitido.", "code": "LOJA_MISMATCH"},
        )


def _to_response(f: dict) -> FaturaResponse:
    loja_info = _MOCK_LOJAS_INFO.get(f["loja_id"], {"nome": "Desconhecida", "morada": "", "telefone": ""})
    return FaturaResponse(
        id=f["id"],
        numero=f["numero"],
        ordem_servico_id=f["ordem_servico_id"],
        data_emissao=f["data_emissao"],
        estado=f["estado"],
        cliente=FaturaClienteInfo(**f["cliente"]),
        trotinete=FaturaTrotineteInfo(**f["trotinete"]),
        servico=FaturaServicoInfo(**f["servico"]),
        pecas_aplicadas=[FaturaPecaAplicada(**p) for p in f["pecas_aplicadas"]],
        subtotal_pecas=f["subtotal_pecas"],
        valor_final=f["valor_final"],
        loja=FaturaLojaInfo(**loja_info),
    )


def _to_resumo(f: dict) -> FaturaResumo:
    return FaturaResumo(
        id=f["id"],
        numero=f["numero"],
        ordem_servico_id=f["ordem_servico_id"],
        cliente_nome=f["cliente"]["nome"],
        cliente_nif=f["cliente"]["nif"],
        valor_final=f["valor_final"],
        data_emissao=f["data_emissao"],
        estado=f["estado"],
    )


# ── Casos de uso ──────────────────────────────────────────────────────────────


def emitir(
    ordem_servico_id: int,
    current_user: CurrentUserResponse,
) -> DataResponse[FaturaResponse]:
    global _next_id

    from app.services.ordem_servico_service import get_os_interna
    from app.services.cliente_service import _find as find_cliente
    from app.services.trotinete_service import _find as find_trotinete
    from app.services.peca_service import get_peca_interna
    from app.schemas.ordem_servico import EstadoOrdemServico as E

    os = get_os_interna(ordem_servico_id)
    if os is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Ordem de serviço não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )

    _check_loja({"loja_id": os["loja_id"]}, current_user)

    if os["fatura_id"] is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Já existe uma fatura para esta ordem de serviço.", "code": "ORDER_ALREADY_INVOICED"},
        )

    if os["estado"] != E.CONCLUIDA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": f"A OS está em estado {os['estado'].value}. Só é possível faturar OS no estado CONCLUIDA.",
                "code": "ORDER_NOT_CONCLUDED",
            },
        )

    cliente = find_cliente(os["cliente_id"])
    trotinete = find_trotinete(os["trotinete_id"])

    pecas_linha: list[dict] = []
    for p in os["pecas_aplicadas"]:
        peca = get_peca_interna(p["peca_id"])
        referencia = peca["referencia"] if peca else f"PEC-{p['peca_id']:03d}"
        pecas_linha.append({
            "peca_referencia": referencia,
            "peca_nome": p["peca_nome"],
            "quantidade": p["quantidade"],
            "preco_venda_unitario": p["preco_venda_unitario"],
            "subtotal": p["subtotal"],
        })

    subtotal_pecas = round(sum(p["subtotal"] for p in pecas_linha), 2)
    valor_final = round(os["preco_servico"] + subtotal_pecas, 2)

    nova = {
        "id": _next_id,
        "numero": f"FAT-2026-{_next_id:04d}",
        "ordem_servico_id": ordem_servico_id,
        "loja_id": os["loja_id"],
        "data_emissao": datetime.now(timezone.utc),
        "estado": EstadoFatura.EMITIDA,
        "cliente": {
            "id": cliente["id"],
            "nome": cliente["nome"],
            "nif": cliente["nif"],
            "morada": cliente.get("morada"),
        },
        "trotinete": {
            "marca": trotinete["marca"],
            "modelo": trotinete["modelo"],
            "numero_serie": trotinete["numero_serie"],
        },
        "servico": {
            "descricao": os["descricao_problema"],
            "preco_servico": os["preco_servico"],
        },
        "pecas_aplicadas": pecas_linha,
        "subtotal_pecas": subtotal_pecas,
        "valor_final": valor_final,
    }

    _MOCK_FATURAS.append(nova)
    os["fatura_id"] = _next_id
    os["estado"] = E.FATURADA
    _next_id += 1

    # [pendente] auditoria FATURA_EMITIDA

    return DataResponse[FaturaResponse](
        data=_to_response(nova),
        message="Fatura emitida com sucesso.",
    )


def obter(
    fatura_id: int,
    current_user: CurrentUserResponse,
) -> DataResponse[FaturaResponse]:
    fatura = _find(fatura_id)
    if fatura is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Fatura não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )
    _check_loja(fatura, current_user)
    return DataResponse[FaturaResponse](data=_to_response(fatura))


def listar(
    ordem_servico_id: int | None,
    loja_id: int | None,
    data_inicio,
    data_fim,
    page: int,
    page_size: int,
    current_user: CurrentUserResponse,
) -> PaginatedResponse[FaturaResumo]:
    itens = list(_MOCK_FATURAS)

    if current_user.perfil != P.ADMINISTRADOR:
        itens = [f for f in itens if f["loja_id"] == current_user.loja_id]
    elif loja_id is not None:
        itens = [f for f in itens if f["loja_id"] == loja_id]

    if ordem_servico_id is not None:
        itens = [f for f in itens if f["ordem_servico_id"] == ordem_servico_id]
    if data_inicio is not None:
        itens = [f for f in itens if f["data_emissao"].date() >= data_inicio]
    if data_fim is not None:
        itens = [f for f in itens if f["data_emissao"].date() <= data_fim]

    total = len(itens)
    pages = max(1, -(-total // page_size))
    start = (page - 1) * page_size

    return PaginatedResponse[FaturaResumo](
        data=[_to_resumo(f) for f in itens[start : start + page_size]],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
