from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.repositories.ordem_servico_repository import OrdemServicoRepository
from app.repositories.auditoria_repository import AuditoriaRepository
from app.repositories.peca_repository import PecaRepository
from app.models.ordem_servico import OrdemServico, OSPeca, EstadoOrdemServico, RegistoTempo, OrdemServicoObservacao
from app.models.servico import OSServico
from app.schemas.auth import CurrentUserResponse
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.auditoria import TipoEventoAuditoria
from app.schemas.common import PaginatedResponse, DataResponse
from app.schemas.ordem_servico import (
    OrdemServicoCreate,
    OrdemServicoResumo,
    OrdemServicoDetalheResponse,
    PecaAplicadaResumo,
    PecaAplicadaResponse,
    _OSClienteInfo,
    _OSTrotineteInfo,
    _OSMecanicoInfo,
    TempoInicioResponse,
    TempoParagemResponse,
    OrdemServicoMecanicoUpdate,
    OrdemServicoObservacaoCreate,
    OrdemServicoObservacaoResponse,
    OSServicoResumo,
    DiagnosticoSubmit,
)

class OrdemServicoService:
    _TRANSICOES = {
        (EstadoOrdemServico.PENDENTE,           EstadoOrdemServico.EM_DIAGNOSTICO):   {PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA, PerfilUtilizador.RECECIONISTA, PerfilUtilizador.MECANICO},
        (EstadoOrdemServico.PENDENTE,           EstadoOrdemServico.CANCELADA):         {PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA, PerfilUtilizador.RECECIONISTA},
        (EstadoOrdemServico.EM_DIAGNOSTICO,     EstadoOrdemServico.AGUARDA_APROVACAO): {PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA, PerfilUtilizador.MECANICO},
        (EstadoOrdemServico.EM_DIAGNOSTICO,     EstadoOrdemServico.CANCELADA):         {PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA},
        (EstadoOrdemServico.AGUARDA_APROVACAO,  EstadoOrdemServico.EM_REPARACAO):      {PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA},
        (EstadoOrdemServico.AGUARDA_APROVACAO,  EstadoOrdemServico.CANCELADA):         {PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA},
        (EstadoOrdemServico.EM_REPARACAO,       EstadoOrdemServico.AGUARDA_PECAS):     {PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA, PerfilUtilizador.MECANICO},
        (EstadoOrdemServico.EM_REPARACAO,       EstadoOrdemServico.CONCLUIDA):         {PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA, PerfilUtilizador.MECANICO},
        (EstadoOrdemServico.EM_REPARACAO,       EstadoOrdemServico.CANCELADA):         {PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA},
        (EstadoOrdemServico.AGUARDA_PECAS,      EstadoOrdemServico.EM_REPARACAO):      {PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA, PerfilUtilizador.MECANICO},
        (EstadoOrdemServico.CONCLUIDA,          EstadoOrdemServico.FATURADA):          {PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA, PerfilUtilizador.RECECIONISTA},
    }

    def _build_peca_resumo(self, op: OSPeca) -> PecaAplicadaResumo:
        return PecaAplicadaResumo(
            peca_id=op.peca_id,
            peca_nome=op.peca.nome,
            quantidade=op.quantidade,
            preco_venda_unitario=op.preco_venda_unitario,
            subtotal=op.quantidade * op.preco_venda_unitario,
        )

    def _build_detalhe_response(self, os: OrdemServico, estado_anterior=None) -> OrdemServicoDetalheResponse:
        pecas = [self._build_peca_resumo(op) for op in os.pecas_aplicadas]
        subtotal_pecas = sum(p.subtotal for p in pecas)
        inicio_timer = next((rt.inicio for rt in os.registos_tempo if rt.fim is None), None)

        prazo = getattr(os, "prazo_estimado", None)
        estados_finais = (EstadoOrdemServico.CONCLUIDA, EstadoOrdemServico.FATURADA, EstadoOrdemServico.CANCELADA)
        if prazo and os.estado not in estados_finais:
            hoje = datetime.now(timezone.utc).date()
            prazo_date = prazo.date() if hasattr(prazo, "date") else prazo
            em_atraso = prazo_date < hoje
            minutos_em_atraso = max(0, (hoje - prazo_date).days * 1440) if em_atraso else 0
        else:
            em_atraso = False
            minutos_em_atraso = 0

        servicos = [
            OSServicoResumo(id=s.id, servico_id=s.servico_id, nome=s.nome, preco=s.preco)
            for s in os.servicos_diagnostico
        ]

        return OrdemServicoDetalheResponse(
            id=os.id,
            numero=os.numero,
            estado=os.estado,
            prioridade=os.prioridade,
            loja_id=os.loja_id,
            loja_nome=os.loja.nome if os.loja else None,
            cliente=_OSClienteInfo.model_validate(os.cliente),
            trotinete=_OSTrotineteInfo.model_validate(os.trotinete),
            mecanico=_OSMecanicoInfo.model_validate(os.mecanico) if os.mecanico else None,
            descricao_problema=os.descricao_problema,
            preco_servico=os.preco_servico,
            servicos_diagnostico=servicos,
            pecas_aplicadas=pecas,
            subtotal_pecas=subtotal_pecas,
            valor_estimado_total=os.preco_servico + subtotal_pecas,
            tempo_total_minutos=os.tempo_total_minutos,
            data_entrada=os.data_entrada,
            data_conclusao=os.data_conclusao,
            fatura_id=os.fatura.id if os.fatura else None,
            em_atraso=em_atraso,
            minutos_em_atraso=minutos_em_atraso,
            inicio_tempo_atual=inicio_timer,
            observacoes=[
                OrdemServicoObservacaoResponse(
                    id=o.id,
                    texto=o.texto,
                    autor_id=o.autor_id,
                    autor_nome=o.autor.nome,
                    criado_em=o.criado_em,
                )
                for o in os.observacoes
            ],
            estado_anterior=estado_anterior,
        )

    def __init__(self, db: Session):
        self.db = db
        self.repo = OrdemServicoRepository(db)
        self.auditoria_repo = AuditoriaRepository(db)
        self.peca_repo = PecaRepository(db)

    def criar(self, body: OrdemServicoCreate, current_user: CurrentUserResponse) -> OrdemServicoDetalheResponse:
        from app.repositories.trotinete_repository import TrotineteRepository

        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and body.loja_id != current_user.loja_id:
            raise HTTPException(status_code=403, detail="Não pode criar OS para outra loja.")

        trot = TrotineteRepository(self.db).get_by_id(body.trotinete_id)
        if not trot:
            raise HTTPException(status_code=404, detail="Trotinete não encontrada.")

        os = self.repo.create(
            trotinete_id=body.trotinete_id,
            cliente_id=trot.cliente_id,
            loja_id=body.loja_id,
            mecanico_id=body.mecanico_id,
            estado=EstadoOrdemServico.PENDENTE,
            prioridade=body.prioridade,
            descricao_problema=body.descricao_problema,
            preco_servico=body.preco_servico,
            data_entrada=datetime.now(timezone.utc),
        )
        self.db.flush()
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.OS_CRIADA,
            descricao=f"OS #{os.numero} criada para trotinete {trot.numero_serie}",
            utilizador_id=current_user.id,
            loja_id=os.loja_id,
            detalhe={"os_id": os.id, "trotinete_id": body.trotinete_id, "mecanico_id": body.mecanico_id, "prioridade": body.prioridade},
        )
        self.db.commit()
        self.db.refresh(os)
        return self._build_detalhe_response(os)

    def _get_os_or_404(self, os_id: int, current_user: CurrentUserResponse) -> OrdemServico:
        os = self.repo.get_by_id(os_id)
        if not os:
            raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada")
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and os.loja_id != current_user.loja_id:
            raise HTTPException(status_code=403, detail="Acesso negado a esta OS")
        return os

    def obter(self, os_id: int, current_user: CurrentUserResponse) -> OrdemServicoDetalheResponse:
        return self._build_detalhe_response(self._get_os_or_404(os_id, current_user))

    def listar(
        self, loja_id: int | None, estado: str | None, mecanico_id: int | None, 
        data_inicio, data_fim, em_atraso: bool, page: int, page_size: int, 
        current_user: CurrentUserResponse
    ):
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
            loja_id = current_user.loja_id

        skip = (page - 1) * page_size
        estado_enum = EstadoOrdemServico(estado) if estado else None
        exclude_timer_not_for = current_user.id if current_user.perfil == PerfilUtilizador.MECANICO else None
        itens, total = self.repo.list(loja_id, estado_enum, mecanico_id, data_inicio, data_fim, skip, page_size, exclude_timer_not_for=exclude_timer_not_for)

        if em_atraso:
            media_minutos = self.db.query(func.avg(OrdemServico.tempo_total_minutos)).filter(
                OrdemServico.estado == EstadoOrdemServico.CONCLUIDA
            ).scalar() or 1440

            agora = datetime.now(timezone.utc)
            itens = [
                os for os in itens
                if os.estado not in [EstadoOrdemServico.CONCLUIDA, EstadoOrdemServico.CANCELADA]
                and (agora - os.data_entrada.replace(tzinfo=timezone.utc)).total_seconds() / 60 > media_minutos
            ]
            total = len(itens)

        pages = max(1, -(-total // page_size))

        os_ids = [os.id for os in itens]
        os_com_timer_ativo: set[int] = set()
        if os_ids:
            ativos = self.db.query(RegistoTempo.ordem_servico_id).filter(
                RegistoTempo.ordem_servico_id.in_(os_ids),
                RegistoTempo.fim.is_(None),
            ).all()
            os_com_timer_ativo = {row[0] for row in ativos}

        resumos = [
            OrdemServicoResumo(
                id=os.id,
                numero=os.numero,
                estado=os.estado,
                prioridade=os.prioridade,
                loja_id=os.loja_id,
                loja_nome=os.loja.nome if os.loja else None,
                cliente_nome=os.cliente.nome if os.cliente else None,
                trotinete_numero_serie=os.trotinete.numero_serie if os.trotinete else None,
                mecanico_nome=os.mecanico.nome if os.mecanico else None,
                data_entrada=os.data_entrada,
                data_conclusao=os.data_conclusao,
                tem_timer_ativo=os.id in os_com_timer_ativo,
            )
            for os in itens
        ]
        return PaginatedResponse[OrdemServicoResumo](
            data=resumos, total=total, page=page, page_size=page_size, pages=pages
        )

    def atualizar_estado(self, os_id: int, novo_estado_str: str, current_user: CurrentUserResponse) -> OrdemServicoDetalheResponse:
        os = self._get_os_or_404(os_id, current_user)
        novo_estado = EstadoOrdemServico(novo_estado_str)
        
        transicao = (os.estado, novo_estado)
        perfis_permitidos = self._TRANSICOES.get(transicao)

        if not perfis_permitidos:
            raise HTTPException(status_code=409, detail="Transição de estado inválida.")
        if current_user.perfil not in perfis_permitidos:
            raise HTTPException(status_code=403, detail="Sem permissão para realizar esta transição.")

        estado_anterior = os.estado
        os.estado = novo_estado
        
        if novo_estado == EstadoOrdemServico.CONCLUIDA:
            os.data_conclusao = datetime.now(timezone.utc)

        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.OS_ESTADO_ALTERADO,
            descricao=f"OS #{os.id} transitou de {estado_anterior.value} para {novo_estado.value}",
            utilizador_id=current_user.id,
            loja_id=os.loja_id,
            detalhe={"os_id": os.id, "de": estado_anterior.value, "para": novo_estado.value}
        )

        self.db.commit()
        self.db.refresh(os)
        return self._build_detalhe_response(os, estado_anterior=estado_anterior)

    def adicionar_peca(self, os_id: int, peca_id: int, quantidade: int, current_user: CurrentUserResponse) -> PecaAplicadaResponse:
        from app.repositories.stock_repository import StockRepository

        os = self._get_os_or_404(os_id, current_user)
        if os.estado in [EstadoOrdemServico.CONCLUIDA, EstadoOrdemServico.CANCELADA]:
            raise HTTPException(status_code=409, detail="Não é possível adicionar peças a uma OS finalizada.")

        peca = self.peca_repo.get_by_id(peca_id)
        if not peca:
            raise HTTPException(status_code=404, detail="Peça não encontrada no catálogo.")

        stock_repo = StockRepository(self.db)
        try:
            stock_repo.consumir(peca.id, os.loja_id, quantidade)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        nova_peca_os = self.repo.adicionar_peca_os(
            os_id=os.id,
            peca_id=peca.id,
            quantidade=quantidade,
            preco_venda_unitario=peca.preco_venda,
        )

        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.OS_PECA_ADICIONADA,
            descricao=f"Peça '{peca.nome}' (x{quantidade}) adicionada à OS #{os.numero}",
            utilizador_id=current_user.id,
            loja_id=os.loja_id,
            detalhe={"os_id": os.id, "peca_id": peca_id, "peca_nome": peca.nome, "quantidade": quantidade},
        )
        self.db.commit()
        self.db.refresh(nova_peca_os)
        return PecaAplicadaResponse(
            peca_id=nova_peca_os.peca_id,
            peca_nome=nova_peca_os.peca.nome,
            quantidade=nova_peca_os.quantidade,
            preco_venda_unitario=nova_peca_os.preco_venda_unitario,
            subtotal=nova_peca_os.quantidade * nova_peca_os.preco_venda_unitario,
        )

    def iniciar_tempo(self, os_id: int, current_user: CurrentUserResponse) -> TempoInicioResponse:
        os = self._get_os_or_404(os_id, current_user)
        if os.estado in [EstadoOrdemServico.CONCLUIDA, EstadoOrdemServico.FATURADA, EstadoOrdemServico.CANCELADA]:
            raise HTTPException(status_code=409, detail="Não é possível iniciar o timer numa OS finalizada.")
        if any(rt.fim is None for rt in os.registos_tempo):
            raise HTTPException(status_code=409, detail="Já existe um timer ativo nesta OS.")
        rt = RegistoTempo(
            ordem_servico_id=os.id,
            inicio=datetime.now(timezone.utc),
            mecanico_id=current_user.id,
        )
        self.db.add(rt)
        self.db.commit()
        return TempoInicioResponse(ordem_servico_id=rt.ordem_servico_id, inicio=rt.inicio)

    def parar_tempo(self, os_id: int, current_user: CurrentUserResponse) -> TempoParagemResponse:
        os = self._get_os_or_404(os_id, current_user)
        rt = next((rt for rt in os.registos_tempo if rt.fim is None), None)
        if not rt:
            raise HTTPException(status_code=409, detail="Não há timer ativo nesta OS.")
        agora = datetime.now(timezone.utc)
        rt.fim = agora
        minutos = int((agora - rt.inicio.replace(tzinfo=timezone.utc)).total_seconds() / 60)
        rt.minutos_esta_sessao = minutos
        acumulado = (os.tempo_total_minutos or 0) + minutos
        rt.tempo_total_acumulado_minutos = acumulado
        os.tempo_total_minutos = acumulado
        self.db.commit()
        return TempoParagemResponse(
            ordem_servico_id=rt.ordem_servico_id,
            inicio=rt.inicio,
            fim=rt.fim,
            minutos_esta_sessao=minutos,
            tempo_total_acumulado_minutos=acumulado,
        )

    def atualizar_mecanico(self, os_id: int, mecanico_id: int | None, current_user: CurrentUserResponse) -> OrdemServicoDetalheResponse:
        os = self._get_os_or_404(os_id, current_user)
        if os.estado in [EstadoOrdemServico.CONCLUIDA, EstadoOrdemServico.FATURADA, EstadoOrdemServico.CANCELADA]:
            raise HTTPException(status_code=409, detail="Não é possível reatribuir mecânico a uma OS finalizada.")
        agora = datetime.now(timezone.utc)
        for rt in os.registos_tempo:
            if rt.fim is None:
                rt.fim = agora
                minutos = int((agora - rt.inicio.replace(tzinfo=timezone.utc)).total_seconds() / 60)
                rt.minutos_esta_sessao = minutos
                acumulado = (os.tempo_total_minutos or 0) + minutos
                rt.tempo_total_acumulado_minutos = acumulado
                os.tempo_total_minutos = acumulado
        os.mecanico_id = mecanico_id
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.OS_MECANICO_ATRIBUIDO,
            descricao=f"Mecânico da OS #{os.numero} atualizado",
            utilizador_id=current_user.id,
            loja_id=os.loja_id,
            detalhe={"os_id": os.id, "mecanico_id": mecanico_id},
        )
        self.db.commit()
        self.db.refresh(os)
        return self._build_detalhe_response(os)

    def submeter_diagnostico(self, os_id: int, body: DiagnosticoSubmit, current_user: CurrentUserResponse) -> OrdemServicoDetalheResponse:
        from app.utils.email import notificar_diagnostico_cliente

        os = self._get_os_or_404(os_id, current_user)
        if os.estado != EstadoOrdemServico.EM_DIAGNOSTICO:
            raise HTTPException(status_code=409, detail="Só é possível submeter diagnóstico numa OS em diagnóstico.")

        # Remove previous diagnostic items if resubmitting
        for s in list(os.servicos_diagnostico):
            self.db.delete(s)

        total = 0.0
        for item in body.itens:
            os_servico = OSServico(
                ordem_servico_id=os.id,
                servico_id=item.servico_id,
                nome=item.nome,
                preco=item.preco,
            )
            self.db.add(os_servico)
            total += item.preco

        os.preco_servico = total
        os.estado = EstadoOrdemServico.EM_REPARACAO

        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.OS_DIAGNOSTICO_SUBMETIDO,
            descricao=f"Diagnóstico submetido para OS #{os.numero} — total {total:.2f} €",
            utilizador_id=current_user.id,
            loja_id=os.loja_id,
            detalhe={"os_id": os.id, "itens": len(body.itens), "total": total},
        )

        self.db.flush()
        self.db.commit()
        self.db.refresh(os)

        # Send email if client has email
        try:
            cliente_email = os.cliente.email if hasattr(os.cliente, 'email') else None
            if cliente_email:
                notificar_diagnostico_cliente(
                    cliente_email=cliente_email,
                    cliente_nome=os.cliente.nome,
                    os_numero=os.numero,
                    loja_nome=os.loja.nome if os.loja else "DLMCare",
                    loja_telefone=os.loja.telefone if os.loja and hasattr(os.loja, 'telefone') else "",
                    servicos=[{"nome": item.nome, "preco": item.preco} for item in body.itens],
                    total=total,
                )
        except Exception:
            pass

        return self._build_detalhe_response(os, estado_anterior=EstadoOrdemServico.EM_DIAGNOSTICO)

    def adicionar_observacao(self, os_id: int, body: OrdemServicoObservacaoCreate, current_user: CurrentUserResponse) -> OrdemServicoObservacaoResponse:
        os = self._get_os_or_404(os_id, current_user)
        if os.estado in (EstadoOrdemServico.CANCELADA, EstadoOrdemServico.FATURADA):
            raise HTTPException(status_code=409, detail="Não é possível adicionar observações a uma OS cancelada ou faturada.")
        obs = self.repo.create_observacao(
            os_id=os.id,
            autor_id=current_user.id,
            texto=body.texto,
            criado_em=datetime.now(timezone.utc),
        )
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.OS_OBSERVACAO_ADICIONADA,
            descricao=f"Observação adicionada à OS #{os.numero}",
            utilizador_id=current_user.id,
            loja_id=os.loja_id,
            detalhe={"os_id": os.id},
        )
        self.db.commit()
        self.db.refresh(obs)
        return OrdemServicoObservacaoResponse(
            id=obs.id,
            texto=obs.texto,
            autor_id=obs.autor_id,
            autor_nome=obs.autor.nome,
            criado_em=obs.criado_em,
        )

    def apagar(self, os_id: int, current_user: CurrentUserResponse) -> None:
        os = self.repo.get_by_id(os_id)
        if not os:
            raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada.")
        self.db.delete(os)
        self.db.commit()