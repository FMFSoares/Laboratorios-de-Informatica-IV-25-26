from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories.fatura_repository import MockFaturaRepository, Fatura
from app.repositories.loja_repository import MockLojaRepository
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
from app.utils.permissions import check_loja_access

_repo = MockFaturaRepository()
_loja_repo = MockLojaRepository()


def _to_response(f: Fatura) -> FaturaResponse:
    loja_info = _loja_repo.as_dict(f.loja_id) or {"nome": "Desconhecida", "morada": "", "telefone": ""}
    return FaturaResponse(
        id=f.id,
        numero=f.numero,
        ordem_servico_id=f.ordem_servico_id,
        data_emissao=f.data_emissao,
        estado=f.estado,
        cliente=FaturaClienteInfo(**f.cliente),
        trotinete=FaturaTrotineteInfo(**f.trotinete),
        servico=FaturaServicoInfo(**f.servico),
        pecas_aplicadas=[FaturaPecaAplicada(**p) for p in f.pecas_aplicadas],
        subtotal_pecas=f.subtotal_pecas,
        valor_final=f.valor_final,
        loja=FaturaLojaInfo(**loja_info),
    )


def _to_resumo(f: Fatura) -> FaturaResumo:
    return FaturaResumo(
        id=f.id,
        numero=f.numero,
        ordem_servico_id=f.ordem_servico_id,
        cliente_nome=f.cliente["nome"],
        cliente_nif=f.cliente["nif"],
        valor_final=f.valor_final,
        data_emissao=f.data_emissao,
        estado=f.estado,
    )


def emitir(
    ordem_servico_id: int,
    current_user: CurrentUserResponse,
) -> DataResponse[FaturaResponse]:
    from app.services.ordem_servico_service import get_os_interna
    from app.services.cliente_service import _find as find_cliente
    from app.services.trotinete_service import _find as find_trotinete
    from app.services.peca_service import get_peca_interna
    from app.schemas.ordem_servico import EstadoOrdemServico as E
    from app.repositories.auditoria_repository import MockAuditoriaRepository
    from app.schemas.auditoria import TipoEventoAuditoria

    os = get_os_interna(ordem_servico_id)
    if os is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Ordem de serviço não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )

    check_loja_access(os.loja_id, current_user)

    if os.fatura_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Já existe uma fatura para esta ordem de serviço.", "code": "ORDER_ALREADY_INVOICED"},
        )

    if os.estado != E.CONCLUIDA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": f"A OS está em estado {os.estado.value}. Só é possível faturar OS no estado CONCLUIDA.",
                "code": "ORDER_NOT_CONCLUDED",
            },
        )

    cliente = find_cliente(os.cliente_id)
    trotinete = find_trotinete(os.trotinete_id)

    pecas_linha: list[dict] = []
    for p in os.pecas_aplicadas:
        peca = get_peca_interna(p["peca_id"])
        referencia = peca.referencia if peca else f"PEC-{p['peca_id']:03d}"
        pecas_linha.append({
            "peca_referencia": referencia,
            "peca_nome": p["peca_nome"],
            "quantidade": p["quantidade"],
            "preco_venda_unitario": p["preco_venda_unitario"],
            "subtotal": p["subtotal"],
        })

    subtotal_pecas = round(sum(p["subtotal"] for p in pecas_linha), 2)
    valor_final = round(os.preco_servico + subtotal_pecas, 2)

    nova = _repo.create(
        ordem_servico_id=ordem_servico_id,
        loja_id=os.loja_id,
        cliente={
            "id": cliente.id,
            "nome": cliente.nome,
            "nif": cliente.nif,
            "morada": cliente.morada,
        },
        trotinete={
            "marca": trotinete.marca,
            "modelo": trotinete.modelo,
            "numero_serie": trotinete.numero_serie,
        },
        servico={
            "descricao": os.descricao_problema,
            "preco_servico": os.preco_servico,
        },
        pecas_aplicadas=pecas_linha,
        subtotal_pecas=subtotal_pecas,
        valor_final=valor_final,
    )

    os.fatura_id = nova.id
    os.estado = E.FATURADA

    MockAuditoriaRepository().registar(
        evento=TipoEventoAuditoria.FATURA_EMITIDA,
        descricao=f"Fatura {nova.numero} emitida para OS #{os.id}.",
        utilizador_id=current_user.id,
        utilizador_nome=current_user.nome,
        loja_id=os.loja_id,
        detalhe={"fatura_id": nova.id, "ordem_servico_id": os.id, "valor_final": valor_final},
    )

    return DataResponse[FaturaResponse](data=_to_response(nova), message="Fatura emitida com sucesso.")


def obter(fatura_id: int, current_user: CurrentUserResponse) -> DataResponse[FaturaResponse]:
    fatura = _repo.get_by_id(fatura_id)
    if fatura is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Fatura não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )
    check_loja_access(fatura.loja_id, current_user)
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
    effective_loja = loja_id if current_user.perfil == P.ADMINISTRADOR else current_user.loja_id
    itens, total = _repo.list(effective_loja, ordem_servico_id, data_inicio, data_fim, page, page_size)
    pages = max(1, -(-total // page_size))

    return PaginatedResponse[FaturaResumo](
        data=[_to_resumo(f) for f in itens],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
