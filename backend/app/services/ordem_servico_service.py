from __future__ import annotations

# [pendente de integração com BD]
# Ordens de serviço em memória para a Etapa 3.

from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.schemas.auth import CurrentUserResponse
from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.ordem_servico import (
    EstadoOrdemServico as E,
    OrdemServicoCreate,
    OrdemServicoDetalheResponse,
    OrdemServicoEstadoUpdate,
    OrdemServicoEstadoUpdateResponse,
    OrdemServicoResponse,
    OrdemServicoResumo,
    PecaAplicadaRequest,
    PecaAplicadaResponse,
    PecaAplicadaResumo,
    PrioridadeOrdemServico,
    TempoInicioResponse,
    TempoParagemResponse,
    _OSClienteInfo,
    _OSMecanicoInfo,
    _OSTrotineteInfo,
)
from app.schemas.utilizador import PerfilUtilizador as P

# ── Tabela de transições: (estado_atual, novo_estado) → perfis autorizados ────

_TRANSICOES: dict[tuple, frozenset] = {
    (E.PENDENTE,          E.EM_DIAGNOSTICO):   frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.MECANICO}),
    (E.PENDENTE,          E.CANCELADA):         frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.RECECIONISTA}),
    (E.EM_DIAGNOSTICO,    E.AGUARDA_APROVACAO): frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.MECANICO}),
    (E.EM_DIAGNOSTICO,    E.CANCELADA):         frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA}),
    (E.AGUARDA_APROVACAO, E.EM_REPARACAO):      frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.RECECIONISTA}),
    (E.AGUARDA_APROVACAO, E.CANCELADA):         frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.RECECIONISTA}),
    (E.EM_REPARACAO,      E.AGUARDA_PECAS):     frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.MECANICO}),
    (E.EM_REPARACAO,      E.CONCLUIDA):         frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.MECANICO}),
    (E.EM_REPARACAO,      E.CANCELADA):         frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA}),
    (E.AGUARDA_PECAS,     E.EM_REPARACAO):      frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.MECANICO}),
    (E.AGUARDA_PECAS,     E.CANCELADA):         frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA}),
    # CONCLUIDA → FATURADA é feita exclusivamente via POST /faturas
}

# ── Mock data ─────────────────────────────────────────────────────────────────

_MOCK_OS: list[dict] = [
    {
        "id": 1,
        "numero": "OS-2026-0001",
        "trotinete_id": 1,
        "cliente_id": 1,
        "loja_id": 1,
        "mecanico_id": 4,
        "estado": E.PENDENTE,
        "prioridade": PrioridadeOrdemServico.NORMAL,
        "descricao_problema": "Não arranca. Bateria parece descarregada mesmo após carga.",
        "preco_servico": 25.00,
        "data_entrada": datetime(2026, 4, 28, 9, 0, tzinfo=timezone.utc),
        "data_conclusao": None,
        "pecas_aplicadas": [],
        "tempo_total_minutos": None,
        "inicio_tempo_atual": None,
        "fatura_id": None,
    },
    {
        "id": 2,
        "numero": "OS-2026-0002",
        "trotinete_id": 2,
        "cliente_id": 2,
        "loja_id": 1,
        "mecanico_id": 4,
        "estado": E.EM_REPARACAO,
        "prioridade": PrioridadeOrdemServico.ALTA,
        "descricao_problema": "Pneu traseiro furado.",
        "preco_servico": 15.00,
        "data_entrada": datetime(2026, 4, 25, 10, 0, tzinfo=timezone.utc),
        "data_conclusao": None,
        "pecas_aplicadas": [
            {
                "peca_id": 2,
                "peca_nome": "Pneu Traseiro 8.5x2 Xiaomi",
                "quantidade": 1,
                "preco_venda_unitario": 18.90,
                "subtotal": 18.90,
            }
        ],
        "tempo_total_minutos": 30,
        "inicio_tempo_atual": None,
        "fatura_id": None,
    },
]

_next_id = 3


# ── Helpers internos ──────────────────────────────────────────────────────────


def _find(os_id: int) -> dict | None:
    return next((o for o in _MOCK_OS if o["id"] == os_id), None)


def get_os_interna(os_id: int) -> dict | None:
    """Exposição pública do _find para fatura_service."""
    return _find(os_id)


def _check_loja(os: dict, current_user: CurrentUserResponse) -> None:
    if current_user.perfil == P.ADMINISTRADOR:
        return
    if os["loja_id"] != current_user.loja_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"detail": "Acesso a dados de outra loja não permitido.", "code": "LOJA_MISMATCH"},
        )


def _404(mensagem: str = "Ordem de serviço não encontrada.") -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"detail": mensagem, "code": "RESOURCE_NOT_FOUND"},
    )


def _pecas_resumo(pecas: list[dict]) -> list[PecaAplicadaResumo]:
    return [PecaAplicadaResumo(**p) for p in pecas]


def _subtotal(pecas: list[dict]) -> float:
    return sum(p["subtotal"] for p in pecas)


def _to_response(os: dict) -> OrdemServicoResponse:
    return OrdemServicoResponse(
        id=os["id"],
        numero=os["numero"],
        trotinete_id=os["trotinete_id"],
        cliente_id=os["cliente_id"],
        loja_id=os["loja_id"],
        mecanico_id=os["mecanico_id"],
        estado=os["estado"],
        prioridade=os["prioridade"],
        descricao_problema=os["descricao_problema"],
        preco_servico=os["preco_servico"],
        data_entrada=os["data_entrada"],
        data_conclusao=os["data_conclusao"],
        pecas_aplicadas=_pecas_resumo(os["pecas_aplicadas"]),
        tempo_total_minutos=os["tempo_total_minutos"],
    )


def _to_resumo(os: dict) -> OrdemServicoResumo:
    from app.services.cliente_service import _find as find_cliente
    from app.services.trotinete_service import _find as find_trotinete
    from app.services.auth_service import _MOCK_USERS
    from app.services.stock_service import _MOCK_LOJAS

    cliente = find_cliente(os["cliente_id"])
    trotinete = find_trotinete(os["trotinete_id"])
    mecanico = next((u for u in _MOCK_USERS if u["id"] == os["mecanico_id"]), None)

    return OrdemServicoResumo(
        id=os["id"],
        numero=os["numero"],
        estado=os["estado"],
        prioridade=os["prioridade"],
        loja_id=os["loja_id"],
        loja_nome=_MOCK_LOJAS.get(os["loja_id"]),
        cliente_nome=cliente["nome"] if cliente else None,
        trotinete_numero_serie=trotinete["numero_serie"] if trotinete else None,
        mecanico_nome=mecanico["nome"] if mecanico else None,
        data_entrada=os["data_entrada"],
    )


def _to_detalhe(os: dict) -> OrdemServicoDetalheResponse:
    from app.services.cliente_service import _find as find_cliente
    from app.services.trotinete_service import _find as find_trotinete
    from app.services.auth_service import _MOCK_USERS
    from app.services.stock_service import _MOCK_LOJAS

    cliente = find_cliente(os["cliente_id"])
    trotinete = find_trotinete(os["trotinete_id"])
    mecanico = (
        next((u for u in _MOCK_USERS if u["id"] == os["mecanico_id"]), None)
        if os["mecanico_id"] else None
    )

    sub = _subtotal(os["pecas_aplicadas"])

    return OrdemServicoDetalheResponse(
        id=os["id"],
        numero=os["numero"],
        estado=os["estado"],
        prioridade=os["prioridade"],
        loja_id=os["loja_id"],
        loja_nome=_MOCK_LOJAS.get(os["loja_id"]),
        cliente=_OSClienteInfo(
            id=cliente["id"], nome=cliente["nome"], telemovel=cliente["telemovel"]
        ),
        trotinete=_OSTrotineteInfo(
            id=trotinete["id"],
            marca=trotinete["marca"],
            modelo=trotinete["modelo"],
            numero_serie=trotinete["numero_serie"],
        ),
        mecanico=_OSMecanicoInfo(id=mecanico["id"], nome=mecanico["nome"]) if mecanico else None,
        descricao_problema=os["descricao_problema"],
        preco_servico=os["preco_servico"],
        pecas_aplicadas=_pecas_resumo(os["pecas_aplicadas"]),
        subtotal_pecas=sub,
        valor_estimado_total=os["preco_servico"] + sub,
        tempo_total_minutos=os["tempo_total_minutos"],
        data_entrada=os["data_entrada"],
        data_conclusao=os["data_conclusao"],
        fatura_id=os["fatura_id"],
    )


# ── Casos de uso ──────────────────────────────────────────────────────────────


def criar(
    body: OrdemServicoCreate,
    current_user: CurrentUserResponse,
) -> DataResponse[OrdemServicoResponse]:
    global _next_id
    from app.services.trotinete_service import _find as find_trotinete
    from app.services.auth_service import _MOCK_USERS

    trotinete = find_trotinete(body.trotinete_id)
    if trotinete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Trotinete não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )

    _check_loja({"loja_id": body.loja_id}, current_user)

    if trotinete["loja_id"] != body.loja_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"detail": "Trotinete pertence a outra loja.", "code": "LOJA_MISMATCH"},
        )

    if body.mecanico_id is not None:
        mecanico = next(
            (u for u in _MOCK_USERS if u["id"] == body.mecanico_id and u["perfil"] == P.MECANICO),
            None,
        )
        if mecanico is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Mecânico não encontrado.", "code": "RESOURCE_NOT_FOUND"},
            )
        if mecanico["loja_id"] != body.loja_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"detail": "Mecânico pertence a outra loja.", "code": "LOJA_MISMATCH"},
            )

    nova = {
        "id": _next_id,
        "numero": f"OS-2026-{_next_id:04d}",
        "trotinete_id": body.trotinete_id,
        "cliente_id": trotinete["cliente_id"],
        "loja_id": body.loja_id,
        "mecanico_id": body.mecanico_id,
        "estado": E.PENDENTE,
        "prioridade": body.prioridade,
        "descricao_problema": body.descricao_problema,
        "preco_servico": body.preco_servico,
        "data_entrada": datetime.now(timezone.utc),
        "data_conclusao": None,
        "pecas_aplicadas": [],
        "tempo_total_minutos": None,
        "inicio_tempo_atual": None,
        "fatura_id": None,
    }
    _MOCK_OS.append(nova)
    _next_id += 1

    return DataResponse[OrdemServicoResponse](
        data=_to_response(nova),
        message="Ordem de serviço criada.",
    )


def listar(
    loja_id: int | None,
    estado: E | None,
    mecanico_id: int | None,
    data_inicio,
    data_fim,
    page: int,
    page_size: int,
    current_user: CurrentUserResponse,
) -> PaginatedResponse[OrdemServicoResumo]:
    itens = list(_MOCK_OS)

    if current_user.perfil != P.ADMINISTRADOR:
        itens = [o for o in itens if o["loja_id"] == current_user.loja_id]
    elif loja_id is not None:
        itens = [o for o in itens if o["loja_id"] == loja_id]

    if estado is not None:
        itens = [o for o in itens if o["estado"] == estado]
    if mecanico_id is not None:
        itens = [o for o in itens if o["mecanico_id"] == mecanico_id]
    if data_inicio is not None:
        itens = [o for o in itens if o["data_entrada"].date() >= data_inicio]
    if data_fim is not None:
        itens = [o for o in itens if o["data_entrada"].date() <= data_fim]

    total = len(itens)
    pages = max(1, -(-total // page_size))
    start = (page - 1) * page_size

    return PaginatedResponse[OrdemServicoResumo](
        data=[_to_resumo(o) for o in itens[start : start + page_size]],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def obter(
    os_id: int,
    current_user: CurrentUserResponse,
) -> DataResponse[OrdemServicoDetalheResponse]:
    os = _find(os_id)
    if os is None:
        _404()
    _check_loja(os, current_user)
    return DataResponse[OrdemServicoDetalheResponse](data=_to_detalhe(os))


def atualizar_estado(
    os_id: int,
    body: OrdemServicoEstadoUpdate,
    current_user: CurrentUserResponse,
) -> DataResponse[OrdemServicoEstadoUpdateResponse]:
    os = _find(os_id)
    if os is None:
        _404()
    _check_loja(os, current_user)

    chave = (os["estado"], body.novo_estado)
    perfis_permitidos = _TRANSICOES.get(chave)

    if perfis_permitidos is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": f"Transição {os['estado'].value} → {body.novo_estado.value} não é permitida.",
                "code": "INVALID_STATE_TRANSITION",
            },
        )

    if current_user.perfil not in perfis_permitidos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"detail": "Sem permissão para esta transição de estado.", "code": "PERMISSION_DENIED"},
        )

    estado_anterior = os["estado"]
    os["estado"] = body.novo_estado
    if body.novo_estado == E.CONCLUIDA:
        os["data_conclusao"] = datetime.now(timezone.utc)

    # [pendente] auditoria OS_ESTADO_ALTERADO

    return DataResponse[OrdemServicoEstadoUpdateResponse](
        data=OrdemServicoEstadoUpdateResponse(
            id=os_id,
            estado_anterior=estado_anterior,
            estado_atual=body.novo_estado,
            alterado_por=current_user.nome,
            data_alteracao=datetime.now(timezone.utc),
        ),
        message="Estado da ordem atualizado.",
    )


def iniciar_tempo(
    os_id: int,
    current_user: CurrentUserResponse,
) -> DataResponse[TempoInicioResponse]:
    os = _find(os_id)
    if os is None:
        _404()
    _check_loja(os, current_user)

    if os["inicio_tempo_atual"] is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Tempo já iniciado. Pare o registo atual primeiro.", "code": "INVALID_STATE_TRANSITION"},
        )

    os["inicio_tempo_atual"] = datetime.now(timezone.utc)

    return DataResponse[TempoInicioResponse](
        data=TempoInicioResponse(ordem_servico_id=os_id, inicio=os["inicio_tempo_atual"]),
        message="Registo de tempo iniciado.",
    )


def parar_tempo(
    os_id: int,
    current_user: CurrentUserResponse,
) -> DataResponse[TempoParagemResponse]:
    os = _find(os_id)
    if os is None:
        _404()
    _check_loja(os, current_user)

    if os["inicio_tempo_atual"] is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Nenhum registo de tempo em curso.", "code": "INVALID_STATE_TRANSITION"},
        )

    fim = datetime.now(timezone.utc)
    inicio = os["inicio_tempo_atual"]
    minutos_sessao = max(0, int((fim - inicio).total_seconds() / 60))
    os["tempo_total_minutos"] = (os["tempo_total_minutos"] or 0) + minutos_sessao
    os["inicio_tempo_atual"] = None

    return DataResponse[TempoParagemResponse](
        data=TempoParagemResponse(
            ordem_servico_id=os_id,
            inicio=inicio,
            fim=fim,
            minutos_esta_sessao=minutos_sessao,
            tempo_total_acumulado_minutos=os["tempo_total_minutos"],
        ),
        message="Registo de tempo parado.",
    )


def adicionar_peca(
    os_id: int,
    body: PecaAplicadaRequest,
    current_user: CurrentUserResponse,
) -> DataResponse[PecaAplicadaResponse]:
    from app.services.peca_service import get_peca_interna
    from app.services.stock_service import consumir_stock

    os = _find(os_id)
    if os is None:
        _404()
    _check_loja(os, current_user)

    if os["estado"] in {E.CONCLUIDA, E.FATURADA, E.CANCELADA}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": f"Não é possível adicionar peças a uma OS em estado {os['estado'].value}.",
                "code": "INVALID_STATE_TRANSITION",
            },
        )

    peca = get_peca_interna(body.peca_id)
    if peca is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Peça não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )

    # Consome stock e lança 400 INSUFFICIENT_STOCK se não houver
    consumir_stock(body.peca_id, os["loja_id"], body.quantidade)

    # Snapshot do preco_venda no momento da aplicação
    preco_venda_unitario = peca["preco_venda"]
    subtotal = body.quantidade * preco_venda_unitario

    # Acumula se a peça já estava na lista
    existente = next((p for p in os["pecas_aplicadas"] if p["peca_id"] == body.peca_id), None)
    if existente:
        existente["quantidade"] += body.quantidade
        existente["subtotal"] = round(existente["subtotal"] + subtotal, 2)
    else:
        os["pecas_aplicadas"].append({
            "peca_id": body.peca_id,
            "peca_nome": peca["nome"],
            "quantidade": body.quantidade,
            "preco_venda_unitario": preco_venda_unitario,
            "subtotal": round(subtotal, 2),
        })

    return DataResponse[PecaAplicadaResponse](
        data=PecaAplicadaResponse(
            peca_id=body.peca_id,
            peca_nome=peca["nome"],
            quantidade=body.quantidade,
            preco_venda_unitario=preco_venda_unitario,
            subtotal=round(subtotal, 2),
        ),
        message="Peça adicionada à ordem de serviço.",
    )
