from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.repositories.ordem_servico_repository import MockOrdemServicoRepository, OrdemServico
from app.repositories.trotinete_repository import MockTrotineteRepository
from app.repositories.utilizador_repository import MockUtilizadorRepository
from app.repositories.loja_repository import MockLojaRepository
from app.repositories.auditoria_repository import MockAuditoriaRepository
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
    OrdemServicoObservacaoCreate,
    OrdemServicoObservacaoResponse,
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
from app.schemas.auditoria import TipoEventoAuditoria
from app.schemas.utilizador import PerfilUtilizador as P
from app.utils.permissions import check_loja_access

_repo = MockOrdemServicoRepository()
_trotinete_repo = MockTrotineteRepository()
_util_repo = MockUtilizadorRepository()
_loja_repo = MockLojaRepository()
_auditoria_repo = MockAuditoriaRepository()

# ── State machine: (current, next) → allowed profiles ────────────────────────

_TRANSICOES: dict[tuple, frozenset] = {
    (E.PENDENTE,          E.EM_DIAGNOSTICO):   frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.MECANICO}),
    (E.PENDENTE,          E.CANCELADA):         frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.RECECIONISTA}),
    (E.EM_DIAGNOSTICO,    E.AGUARDA_APROVACAO): frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA}),
    (E.EM_DIAGNOSTICO,    E.EM_REPARACAO):      frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.MECANICO}),
    (E.EM_DIAGNOSTICO,    E.CANCELADA):         frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA}),
    (E.AGUARDA_APROVACAO, E.EM_REPARACAO):      frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.RECECIONISTA}),
    (E.AGUARDA_APROVACAO, E.CANCELADA):         frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.RECECIONISTA}),
    (E.EM_REPARACAO,      E.AGUARDA_PECAS):     frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.MECANICO}),
    (E.EM_REPARACAO,      E.CONCLUIDA):         frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.MECANICO}),
    (E.EM_REPARACAO,      E.CANCELADA):         frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA}),
    (E.AGUARDA_PECAS,     E.EM_REPARACAO):      frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA, P.MECANICO}),
    (E.AGUARDA_PECAS,     E.CANCELADA):         frozenset({P.ADMINISTRADOR, P.GERENTE_LOJA}),
    # CONCLUIDA → FATURADA happens exclusively via POST /faturas
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_os_interna(os_id: int) -> OrdemServico | None:
    """Public cross-service accessor used by fatura_service."""
    return _repo.get_by_id(os_id)


def _404(msg: str = "Ordem de serviço não encontrada.") -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"detail": msg, "code": "RESOURCE_NOT_FOUND"},
    )


def _pecas_resumo(pecas: list[dict]) -> list[PecaAplicadaResumo]:
    return [PecaAplicadaResumo(**p) for p in pecas]


def _subtotal(pecas: list[dict]) -> float:
    return sum(p["subtotal"] for p in pecas)


def _media_minutos_reparacao() -> float | None:
    concluidas = [
        o for o in _repo.list_all()
        if o.estado in {E.CONCLUIDA, E.FATURADA} and o.data_conclusao is not None
    ]
    if not concluidas:
        return None
    total = sum(
        (o.data_conclusao - o.data_entrada).total_seconds() / 60
        for o in concluidas
    )
    return total / len(concluidas)


def _atraso(os: OrdemServico) -> tuple[bool, int | None]:
    if os.estado in {E.CONCLUIDA, E.FATURADA, E.CANCELADA}:
        return False, None
    media = _media_minutos_reparacao()
    if media is None:
        return False, None
    decorridos = (datetime.now(timezone.utc) - os.data_entrada).total_seconds() / 60
    if decorridos > media:
        return True, int(decorridos - media)
    return False, None


def _to_response(os: OrdemServico) -> OrdemServicoResponse:
    return OrdemServicoResponse(
        id=os.id,
        numero=os.numero,
        trotinete_id=os.trotinete_id,
        cliente_id=os.cliente_id,
        loja_id=os.loja_id,
        mecanico_id=os.mecanico_id,
        estado=os.estado,
        prioridade=os.prioridade,
        descricao_problema=os.descricao_problema,
        preco_servico=os.preco_servico,
        data_entrada=os.data_entrada,
        data_conclusao=os.data_conclusao,
        pecas_aplicadas=_pecas_resumo(os.pecas_aplicadas),
        tempo_total_minutos=os.tempo_total_minutos,
    )


def _to_resumo(os: OrdemServico) -> OrdemServicoResumo:
    from app.services.cliente_service import _find as find_cliente

    cliente = find_cliente(os.cliente_id)
    trotinete = _trotinete_repo.get_by_id(os.trotinete_id)
    mecanico = _util_repo.get_by_id(os.mecanico_id) if os.mecanico_id else None
    em_atraso, minutos_em_atraso = _atraso(os)

    return OrdemServicoResumo(
        id=os.id,
        numero=os.numero,
        estado=os.estado,
        prioridade=os.prioridade,
        loja_id=os.loja_id,
        loja_nome=_loja_repo.get_nome(os.loja_id),
        cliente_nome=cliente.nome if cliente else None,
        trotinete_numero_serie=trotinete.numero_serie if trotinete else None,
        mecanico_nome=mecanico.nome if mecanico else None,
        data_entrada=os.data_entrada,
        data_conclusao=os.data_conclusao,
        em_atraso=em_atraso,
        minutos_em_atraso=minutos_em_atraso,
        tem_timer_ativo=os.inicio_tempo_atual is not None,
    )


def _to_detalhe(os: OrdemServico) -> OrdemServicoDetalheResponse:
    from app.services.cliente_service import _find as find_cliente

    cliente = find_cliente(os.cliente_id)
    trotinete = _trotinete_repo.get_by_id(os.trotinete_id)
    mecanico = _util_repo.get_by_id(os.mecanico_id) if os.mecanico_id else None
    sub = _subtotal(os.pecas_aplicadas)
    em_atraso, minutos_em_atraso = _atraso(os)

    return OrdemServicoDetalheResponse(
        id=os.id,
        numero=os.numero,
        estado=os.estado,
        prioridade=os.prioridade,
        loja_id=os.loja_id,
        loja_nome=_loja_repo.get_nome(os.loja_id),
        cliente=_OSClienteInfo(id=cliente.id, nome=cliente.nome, telemovel=cliente.telemovel),
        trotinete=_OSTrotineteInfo(
            id=trotinete.id,
            marca=trotinete.marca,
            modelo=trotinete.modelo,
            numero_serie=trotinete.numero_serie,
        ),
        mecanico=_OSMecanicoInfo(id=mecanico.id, nome=mecanico.nome) if mecanico else None,
        descricao_problema=os.descricao_problema,
        preco_servico=os.preco_servico,
        pecas_aplicadas=_pecas_resumo(os.pecas_aplicadas),
        subtotal_pecas=sub,
        valor_estimado_total=os.preco_servico + sub,
        tempo_total_minutos=os.tempo_total_minutos,
        data_entrada=os.data_entrada,
        data_conclusao=os.data_conclusao,
        fatura_id=os.fatura_id,
        em_atraso=em_atraso,
        minutos_em_atraso=minutos_em_atraso,
        inicio_tempo_atual=os.inicio_tempo_atual,
        observacoes=[OrdemServicoObservacaoResponse(**o) for o in os.observacoes],
    )


# ── Use cases ─────────────────────────────────────────────────────────────────

def criar(body: OrdemServicoCreate, current_user: CurrentUserResponse) -> DataResponse[OrdemServicoResponse]:
    trotinete = _trotinete_repo.get_by_id(body.trotinete_id)
    if trotinete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Trotinete não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )

    check_loja_access(body.loja_id, current_user)

    if trotinete.loja_id != body.loja_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"detail": "Trotinete pertence a outra loja.", "code": "LOJA_MISMATCH"},
        )

    if body.mecanico_id is not None:
        mecanico = _util_repo.get_by_id(body.mecanico_id)
        if mecanico is None or mecanico.perfil != P.MECANICO:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Mecânico não encontrado.", "code": "RESOURCE_NOT_FOUND"},
            )
        if mecanico.loja_id != body.loja_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"detail": "Mecânico pertence a outra loja.", "code": "LOJA_MISMATCH"},
            )

    nova = _repo.create(
        trotinete_id=body.trotinete_id,
        cliente_id=trotinete.cliente_id,
        loja_id=body.loja_id,
        mecanico_id=body.mecanico_id,
        estado=E.PENDENTE,
        prioridade=body.prioridade,
        descricao_problema=body.descricao_problema,
        preco_servico=body.preco_servico,
    )

    return DataResponse[OrdemServicoResponse](data=_to_response(nova), message="Ordem de serviço criada.")


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
    effective_loja = loja_id if current_user.perfil == P.ADMINISTRADOR else current_user.loja_id
    itens, total = _repo.list(effective_loja, estado, mecanico_id, data_inicio, data_fim, 1, 10_000)

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


def obter(os_id: int, current_user: CurrentUserResponse) -> DataResponse[OrdemServicoDetalheResponse]:
    os = _repo.get_by_id(os_id)
    if os is None:
        _404()
    check_loja_access(os.loja_id, current_user)
    return DataResponse[OrdemServicoDetalheResponse](data=_to_detalhe(os))


def atualizar_estado(
    os_id: int,
    body: OrdemServicoEstadoUpdate,
    current_user: CurrentUserResponse,
    background_tasks=None,
) -> DataResponse[OrdemServicoEstadoUpdateResponse]:
    os = _repo.get_by_id(os_id)
    if os is None:
        _404()
    check_loja_access(os.loja_id, current_user)

    chave = (os.estado, body.novo_estado)
    perfis_permitidos = _TRANSICOES.get(chave)

    if perfis_permitidos is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": f"Transição {os.estado.value} → {body.novo_estado.value} não é permitida.",
                "code": "INVALID_STATE_TRANSITION",
            },
        )

    if current_user.perfil not in perfis_permitidos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"detail": "Sem permissão para esta transição de estado.", "code": "PERMISSION_DENIED"},
        )

    estado_anterior = os.estado
    os.estado = body.novo_estado

    _ESTADOS_INICIO_TIMER = {E.EM_DIAGNOSTICO, E.EM_REPARACAO}
    _ESTADOS_PARAGEM_TIMER = {E.AGUARDA_APROVACAO, E.AGUARDA_PECAS, E.CONCLUIDA, E.CANCELADA}

    if current_user.perfil == P.MECANICO:
        if os.mecanico_id is None:
            os.mecanico_id = current_user.id

        if body.novo_estado in _ESTADOS_INICIO_TIMER:
            for other in _repo.list_by_mecanico(os.mecanico_id):
                if other.id != os_id and other.inicio_tempo_atual is not None:
                    fim = datetime.now(timezone.utc)
                    mins = max(0, int((fim - other.inicio_tempo_atual).total_seconds() / 60))
                    other.tempo_total_minutos = (other.tempo_total_minutos or 0) + mins
                    other.inicio_tempo_atual = None
            if os.inicio_tempo_atual is None:
                os.inicio_tempo_atual = datetime.now(timezone.utc)

        elif body.novo_estado in _ESTADOS_PARAGEM_TIMER and os.inicio_tempo_atual is not None:
            fim = datetime.now(timezone.utc)
            mins = max(0, int((fim - os.inicio_tempo_atual).total_seconds() / 60))
            os.tempo_total_minutos = (os.tempo_total_minutos or 0) + mins
            os.inicio_tempo_atual = None

    if body.novo_estado == E.CONCLUIDA:
        os.data_conclusao = datetime.now(timezone.utc)
        _notificar_cliente_trotinete_pronta(os, background_tasks)
    elif body.novo_estado == E.CANCELADA:
        _notificar_cliente_os_cancelada(os, background_tasks)

    if body.observacao:
        _TRANSITION_LABELS = {
            E.EM_REPARACAO:  "Conclusão do Diagnóstico",
            E.CONCLUIDA:     "Conclusão da Reparação",
            E.CANCELADA:     "Cancelamento",
        }
        label = _TRANSITION_LABELS.get(body.novo_estado)
        texto = f"[{label}] {body.observacao}" if label else body.observacao
        _repo.adicionar_observacao(os_id, texto, current_user.id, current_user.nome)

    _auditoria_repo.registar(
        evento=TipoEventoAuditoria.OS_ESTADO_ALTERADO,
        descricao=f"OS #{os.id} alterada de {estado_anterior.value} para {body.novo_estado.value}.",
        utilizador_id=current_user.id,
        utilizador_nome=current_user.nome,
        loja_id=os.loja_id,
        detalhe={"ordem_servico_id": os.id, "estado_anterior": estado_anterior.value, "estado_novo": body.novo_estado.value},
    )

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


def _notificar_cliente_trotinete_pronta(os: OrdemServico, background_tasks) -> None:
    from app.services.cliente_service import _find as find_cliente
    from app.utils.email import notificar_trotinete_pronta

    cliente = find_cliente(os.cliente_id)
    if not cliente or not cliente.email:
        return

    loja_nome = _loja_repo.get_nome(os.loja_id) or "DLMCare"
    loja_telefone = _loja_repo.get_telefone(os.loja_id) or "210 000 000"

    if background_tasks is not None:
        background_tasks.add_task(
            notificar_trotinete_pronta,
            cliente_email=cliente.email,
            cliente_nome=cliente.nome,
            os_numero=os.numero,
            loja_nome=loja_nome,
            loja_telefone=loja_telefone,
        )
    else:
        notificar_trotinete_pronta(
            cliente_email=cliente.email,
            cliente_nome=cliente.nome,
            os_numero=os.numero,
            loja_nome=loja_nome,
            loja_telefone=loja_telefone,
        )


def _notificar_cliente_os_cancelada(os: OrdemServico, background_tasks) -> None:
    from app.services.cliente_service import _find as find_cliente
    from app.utils.email import notificar_os_cancelada

    cliente = find_cliente(os.cliente_id)
    if not cliente or not cliente.email:
        return

    loja_nome = _loja_repo.get_nome(os.loja_id) or "DLMCare"
    loja_telefone = _loja_repo.get_telefone(os.loja_id) or "210 000 000"

    if background_tasks is not None:
        background_tasks.add_task(
            notificar_os_cancelada,
            cliente_email=cliente.email,
            cliente_nome=cliente.nome,
            os_numero=os.numero,
            loja_nome=loja_nome,
            loja_telefone=loja_telefone,
        )
    else:
        notificar_os_cancelada(
            cliente_email=cliente.email,
            cliente_nome=cliente.nome,
            os_numero=os.numero,
            loja_nome=loja_nome,
            loja_telefone=loja_telefone,
        )


def atualizar_mecanico(
    os_id: int,
    body: OrdemServicoMecanicoUpdate,
    current_user: CurrentUserResponse,
) -> DataResponse[OrdemServicoMecanicoUpdateResponse]:
    os = _repo.get_by_id(os_id)
    if os is None:
        _404()
    check_loja_access(os.loja_id, current_user)

    if os.estado in {E.CONCLUIDA, E.FATURADA, E.CANCELADA}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": f"Não é possível reatribuir mecânico a uma OS em estado {os.estado.value}.", "code": "INVALID_STATE_TRANSITION"},
        )

    mecanico_nome = None
    if body.mecanico_id is not None:
        mecanico = _util_repo.get_by_id(body.mecanico_id)
        if mecanico is None or mecanico.perfil != P.MECANICO:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "Mecânico não encontrado.", "code": "RESOURCE_NOT_FOUND"},
            )
        if mecanico.loja_id != os.loja_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"detail": "Mecânico pertence a outra loja.", "code": "LOJA_MISMATCH"},
            )
        mecanico_nome = mecanico.nome

    os.mecanico_id = body.mecanico_id

    return DataResponse[OrdemServicoMecanicoUpdateResponse](
        data=OrdemServicoMecanicoUpdateResponse(
            id=os_id,
            mecanico_id=body.mecanico_id,
            mecanico_nome=mecanico_nome,
        ),
        message="Mecânico atualizado." if body.mecanico_id else "Mecânico desatribuído.",
    )


def iniciar_tempo(os_id: int, current_user: CurrentUserResponse) -> DataResponse[TempoInicioResponse]:
    os = _repo.get_by_id(os_id)
    if os is None:
        _404()
    check_loja_access(os.loja_id, current_user)

    if os.inicio_tempo_atual is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Tempo já iniciado. Pare o registo atual primeiro.", "code": "INVALID_STATE_TRANSITION"},
        )

    if os.mecanico_id is not None:
        conflito = next(
            (o for o in _repo.list_by_mecanico(os.mecanico_id) if o.id != os_id and o.inicio_tempo_atual is not None),
            None,
        )
        if conflito is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "detail": f"O mecânico já tem um registo de tempo ativo na OS {conflito.numero}. Pare esse registo antes de iniciar um novo.",
                    "code": "MECANICO_TIMER_CONFLICT",
                    "os_conflito_id": conflito.id,
                    "os_conflito_numero": conflito.numero,
                },
            )

    os.inicio_tempo_atual = datetime.now(timezone.utc)

    return DataResponse[TempoInicioResponse](
        data=TempoInicioResponse(ordem_servico_id=os_id, inicio=os.inicio_tempo_atual),
        message="Registo de tempo iniciado.",
    )


def parar_tempo(os_id: int, current_user: CurrentUserResponse) -> DataResponse[TempoParagemResponse]:
    os = _repo.get_by_id(os_id)
    if os is None:
        _404()
    check_loja_access(os.loja_id, current_user)

    if os.inicio_tempo_atual is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Nenhum registo de tempo em curso.", "code": "INVALID_STATE_TRANSITION"},
        )

    fim = datetime.now(timezone.utc)
    inicio = os.inicio_tempo_atual
    minutos_sessao = max(0, int((fim - inicio).total_seconds() / 60))
    os.tempo_total_minutos = (os.tempo_total_minutos or 0) + minutos_sessao
    os.inicio_tempo_atual = None

    return DataResponse[TempoParagemResponse](
        data=TempoParagemResponse(
            ordem_servico_id=os_id,
            inicio=inicio,
            fim=fim,
            minutos_esta_sessao=minutos_sessao,
            tempo_total_acumulado_minutos=os.tempo_total_minutos,
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

    os = _repo.get_by_id(os_id)
    if os is None:
        _404()
    check_loja_access(os.loja_id, current_user)

    if os.estado in {E.CONCLUIDA, E.FATURADA, E.CANCELADA}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": f"Não é possível adicionar peças a uma OS em estado {os.estado.value}.", "code": "INVALID_STATE_TRANSITION"},
        )

    peca = get_peca_interna(body.peca_id)
    if peca is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": "Peça não encontrada.", "code": "RESOURCE_NOT_FOUND"},
        )

    consumir_stock(body.peca_id, os.loja_id, body.quantidade)

    preco_venda_unitario = peca.preco_venda
    subtotal = round(body.quantidade * preco_venda_unitario, 2)

    existente = next((p for p in os.pecas_aplicadas if p["peca_id"] == body.peca_id), None)
    if existente:
        existente["quantidade"] += body.quantidade
        existente["subtotal"] = round(existente["subtotal"] + subtotal, 2)
    else:
        os.pecas_aplicadas.append({
            "peca_id": body.peca_id,
            "peca_nome": peca.nome,
            "quantidade": body.quantidade,
            "preco_venda_unitario": preco_venda_unitario,
            "subtotal": subtotal,
        })

    return DataResponse[PecaAplicadaResponse](
        data=PecaAplicadaResponse(
            peca_id=body.peca_id,
            peca_nome=peca.nome,
            quantidade=body.quantidade,
            preco_venda_unitario=preco_venda_unitario,
            subtotal=subtotal,
        ),
        message="Peça adicionada à ordem de serviço.",
    )


def adicionar_observacao(
    os_id: int,
    body: OrdemServicoObservacaoCreate,
    current_user: CurrentUserResponse,
) -> DataResponse[OrdemServicoObservacaoResponse]:
    os = _repo.get_by_id(os_id)
    if os is None:
        _404()
    check_loja_access(os.loja_id, current_user)

    if os.estado == E.CANCELADA:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Não é possível adicionar observações a uma OS cancelada.", "code": "INVALID_STATE_TRANSITION"},
        )

    obs = _repo.adicionar_observacao(os_id, body.texto, current_user.id, current_user.nome)

    return DataResponse[OrdemServicoObservacaoResponse](
        data=OrdemServicoObservacaoResponse(**obs),
        message="Observação adicionada.",
    )
