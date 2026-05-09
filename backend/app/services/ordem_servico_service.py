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
    OrdemServicoMecanicoUpdate,
    OrdemServicoMecanicoUpdateResponse,
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
from app.utils.permissions import check_loja_access

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



def _404(mensagem: str = "Ordem de serviço não encontrada.") -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"detail": mensagem, "code": "RESOURCE_NOT_FOUND"},
    )


def _pecas_resumo(pecas: list[dict]) -> list[PecaAplicadaResumo]:
    return [PecaAplicadaResumo(**p) for p in pecas]


def _subtotal(pecas: list[dict]) -> float:
    return sum(p["subtotal"] for p in pecas)


def _media_minutos_reparacao() -> float | None:
    """Average elapsed calendar minutes across all CONCLUIDA/FATURADA OS."""
    concluidas = [
        o for o in _MOCK_OS
        if o["estado"] in {E.CONCLUIDA, E.FATURADA} and o["data_conclusao"] is not None
    ]
    if not concluidas:
        return None
    total = sum(
        (o["data_conclusao"] - o["data_entrada"]).total_seconds() / 60
        for o in concluidas
    )
    return total / len(concluidas)


def _atraso(os: dict) -> tuple[bool, int | None]:
    """Returns (em_atraso, minutos_em_atraso) for an open OS."""
    if os["estado"] in {E.CONCLUIDA, E.FATURADA, E.CANCELADA}:
        return False, None
    media = _media_minutos_reparacao()
    if media is None:
        return False, None
    decorridos = (datetime.now(timezone.utc) - os["data_entrada"]).total_seconds() / 60
    if decorridos > media:
        return True, int(decorridos - media)
    return False, None


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
    from app.services.loja_service import get_nome as _get_loja_nome

    cliente = find_cliente(os["cliente_id"])
    trotinete = find_trotinete(os["trotinete_id"])
    mecanico = next((u for u in _MOCK_USERS if u["id"] == os["mecanico_id"]), None)
    em_atraso, minutos_em_atraso = _atraso(os)

    return OrdemServicoResumo(
        id=os["id"],
        numero=os["numero"],
        estado=os["estado"],
        prioridade=os["prioridade"],
        loja_id=os["loja_id"],
        loja_nome=_get_loja_nome(os["loja_id"]),
        cliente_nome=cliente.nome if cliente else None,
        trotinete_numero_serie=trotinete["numero_serie"] if trotinete else None,
        mecanico_nome=mecanico["nome"] if mecanico else None,
        data_entrada=os["data_entrada"],
        em_atraso=em_atraso,
        minutos_em_atraso=minutos_em_atraso,
    )


def _to_detalhe(os: dict) -> OrdemServicoDetalheResponse:
    from app.services.cliente_service import _find as find_cliente
    from app.services.trotinete_service import _find as find_trotinete
    from app.services.auth_service import _MOCK_USERS
    from app.services.loja_service import get_nome as _get_loja_nome

    cliente = find_cliente(os["cliente_id"])
    trotinete = find_trotinete(os["trotinete_id"])
    mecanico = (
        next((u for u in _MOCK_USERS if u["id"] == os["mecanico_id"]), None)
        if os["mecanico_id"] else None
    )

    sub = _subtotal(os["pecas_aplicadas"])
    em_atraso, minutos_em_atraso = _atraso(os)

    return OrdemServicoDetalheResponse(
        id=os["id"],
        numero=os["numero"],
        estado=os["estado"],
        prioridade=os["prioridade"],
        loja_id=os["loja_id"],
        loja_nome=_get_loja_nome(os["loja_id"]),
        cliente=_OSClienteInfo(
            id=cliente.id, nome=cliente.nome, telemovel=cliente.telemovel
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
        em_atraso=em_atraso,
        minutos_em_atraso=minutos_em_atraso,
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

    check_loja_access(body.loja_id, current_user)

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
    em_atraso: bool | None,
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
    if em_atraso is not None:
        itens = [o for o in itens if _atraso(o)[0] == em_atraso]

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
    check_loja_access(os["loja_id"], current_user)
    return DataResponse[OrdemServicoDetalheResponse](data=_to_detalhe(os))


def atualizar_estado(
    os_id: int,
    body: OrdemServicoEstadoUpdate,
    current_user: CurrentUserResponse,
    background_tasks=None,
) -> DataResponse[OrdemServicoEstadoUpdateResponse]:
    os = _find(os_id)
    if os is None:
        _404()
    check_loja_access(os["loja_id"], current_user)

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
        _notificar_cliente_trotinete_pronta(os, background_tasks)

    from app.services.auditoria_service import _MOCK_AUDITORIA
    from app.schemas.auditoria import TipoEventoAuditoria

    _MOCK_AUDITORIA.append({
        "id": len(_MOCK_AUDITORIA) + 1,
        "evento": TipoEventoAuditoria.OS_ESTADO_ALTERADO,
        "descricao": f"OS #{os['id']} alterada de {estado_anterior.value} para {body.novo_estado.value}.",
        "utilizador_id": current_user.id,
        "utilizador_nome": current_user.nome,
        "loja_id": os["loja_id"],
        "ip_origem": "127.0.0.1",
        "timestamp": datetime.now(timezone.utc),
        "detalhe": {"ordem_servico_id": os["id"], "estado_anterior": estado_anterior.value, "estado_novo": body.novo_estado.value},
    })

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


def _notificar_cliente_trotinete_pronta(os: dict, background_tasks) -> None:
    from app.services.cliente_service import _find as find_cliente
    from app.services.loja_service import get_nome as _get_loja_nome
    from app.utils.email import notificar_trotinete_pronta

    cliente = find_cliente(os["cliente_id"])
    if not cliente or not cliente.email:
        return

    from app.services.loja_service import get_telefone as _get_loja_telefone
    loja_nome = _get_loja_nome(os["loja_id"]) or "DLMCare"
    loja_telefone = _get_loja_telefone(os["loja_id"]) or "210 000 000"

    if background_tasks is not None:
        background_tasks.add_task(
            notificar_trotinete_pronta,
            cliente_email=cliente.email,
            cliente_nome=cliente.nome,
            os_numero=os["numero"],
            loja_nome=loja_nome,
            loja_telefone=loja_telefone,
        )
    else:
        notificar_trotinete_pronta(
            cliente_email=cliente.email,
            cliente_nome=cliente.nome,
            os_numero=os["numero"],
            loja_nome=loja_nome,
            loja_telefone=loja_telefone,
        )


def atualizar_mecanico(
    os_id: int,
    body: OrdemServicoMecanicoUpdate,
    current_user: CurrentUserResponse,
) -> DataResponse[OrdemServicoMecanicoUpdateResponse]:
    from app.services.auth_service import _MOCK_USERS

    os = _find(os_id)
    if os is None:
        _404()
    check_loja_access(os["loja_id"], current_user)

    if os["estado"] in {E.CONCLUIDA, E.FATURADA, E.CANCELADA}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": f"Não é possível reatribuir mecânico a uma OS em estado {os['estado'].value}.", "code": "INVALID_STATE_TRANSITION"},
        )

    mecanico_nome = None
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
        if mecanico["loja_id"] != os["loja_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"detail": "Mecânico pertence a outra loja.", "code": "LOJA_MISMATCH"},
            )
        mecanico_nome = mecanico["nome"]

    os["mecanico_id"] = body.mecanico_id

    return DataResponse[OrdemServicoMecanicoUpdateResponse](
        data=OrdemServicoMecanicoUpdateResponse(
            id=os_id,
            mecanico_id=body.mecanico_id,
            mecanico_nome=mecanico_nome,
        ),
        message="Mecânico atualizado." if body.mecanico_id else "Mecânico desatribuído.",
    )


def iniciar_tempo(
    os_id: int,
    current_user: CurrentUserResponse,
) -> DataResponse[TempoInicioResponse]:
    os = _find(os_id)
    if os is None:
        _404()
    check_loja_access(os["loja_id"], current_user)

    if os["inicio_tempo_atual"] is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Tempo já iniciado. Pare o registo atual primeiro.", "code": "INVALID_STATE_TRANSITION"},
        )

    mecanico_id = os["mecanico_id"]
    if mecanico_id is not None:
        conflito = next(
            (
                o for o in _MOCK_OS
                if o["id"] != os_id
                and o["mecanico_id"] == mecanico_id
                and o["inicio_tempo_atual"] is not None
            ),
            None,
        )
        if conflito is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "detail": f"O mecânico já tem um registo de tempo ativo na OS {conflito['numero']}. Pare esse registo antes de iniciar um novo.",
                    "code": "MECANICO_TIMER_CONFLICT",
                    "os_conflito_id": conflito["id"],
                    "os_conflito_numero": conflito["numero"],
                },
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
    check_loja_access(os["loja_id"], current_user)

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
    check_loja_access(os["loja_id"], current_user)

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
