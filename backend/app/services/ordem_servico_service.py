from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.repositories.ordem_servico_repository import OrdemServicoRepository
from app.repositories.auditoria_repository import AuditoriaRepository
from app.repositories.peca_repository import PecaRepository
from app.models.ordem_servico import OrdemServico, EstadoOrdemServico, RegistoTempo
from app.schemas.auth import CurrentUserResponse
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.auditoria import TipoEventoAuditoria
from app.schemas.common import PaginatedResponse, DataResponse

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

    def __init__(self, db: Session):
        self.db = db
        self.repo = OrdemServicoRepository(db)
        self.auditoria_repo = AuditoriaRepository(db)
        self.peca_repo = PecaRepository(db)

    def obter(self, os_id: int, current_user: CurrentUserResponse) -> OrdemServico:
        os = self.repo.get_by_id(os_id)
        if not os:
            raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada")
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and os.loja_id != current_user.loja_id:
            raise HTTPException(status_code=403, detail="Acesso negado a esta OS")
        return os

    def listar(
        self, loja_id: int | None, estado: str | None, mecanico_id: int | None, 
        data_inicio, data_fim, em_atraso: bool, page: int, page_size: int, 
        current_user: CurrentUserResponse
    ):
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
            loja_id = current_user.loja_id

        skip = (page - 1) * page_size
        estado_enum = EstadoOrdemServico(estado) if estado else None
        itens, total = self.repo.list(loja_id, estado_enum, mecanico_id, data_inicio, data_fim, skip, page_size)

        # Aplicação da Lógica de Negócio (RF17): OS em Atraso (Filtro em Python)
        if em_atraso:
            # Exemplo: Calcula a média do tempo_total_minutos de todas as OS Concluídas globalmente
            media_minutos = self.db.query(func.avg(OrdemServico.tempo_total_minutos)).filter(
                OrdemServico.estado == EstadoOrdemServico.CONCLUIDA
            ).scalar() or 1440  # Fallback de 24h se não houverem OS concluídas
            
            agora = datetime.now(timezone.utc)
            # Filtra itens que ainda não estão concluídos e cujo tempo ultrapassa a média
            itens = [
                os for os in itens 
                if os.estado not in [EstadoOrdemServico.CONCLUIDA, EstadoOrdemServico.CANCELADA] 
                and (agora - os.data_entrada.replace(tzinfo=timezone.utc)).total_seconds() / 60 > media_minutos
            ]
            total = len(itens)

        pages = max(1, -(-total // page_size))
        # Aqui deves mapear a resposta para OrdemServicoResumo conforme schema
        return {"data": itens, "total": total, "page": page, "page_size": page_size, "pages": pages}

    def atualizar_estado(self, os_id: int, novo_estado_str: str, current_user: CurrentUserResponse):
        os = self.obter(os_id, current_user)
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

        # Integração com a Auditoria na mesma transação
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.ATUALIZACAO, # ou OS_ESTADO_ALTERADO se constar no teu Schema
            descricao=f"OS #{os.id} transitou de {estado_anterior.value} para {novo_estado.value}",
            utilizador_id=current_user.id,
            loja_id=os.loja_id,
            detalhe={"os_id": os.id, "de": estado_anterior.value, "para": novo_estado.value}
        )

        self.db.commit()
        self.db.refresh(os)
        return os

    def adicionar_peca(self, os_id: int, peca_id: int, quantidade: int, current_user: CurrentUserResponse):
        from app.services.stock_service import StockService # Import local para prevenir circularidade

        os = self.obter(os_id, current_user)
        if os.estado in [EstadoOrdemServico.CONCLUIDA, EstadoOrdemServico.CANCELADA]:
            raise HTTPException(status_code=409, detail="Não é possível adicionar peças a uma OS finalizada.")

        peca = self.peca_repo.get_by_id(peca_id)
        if not peca:
            raise HTTPException(status_code=404, detail="Peça não encontrada no catálogo.")

        # 1. Consumir stock na base de dados (A lógica do stock service irá efetuar self.db.add() mas NÃO o commit global)
        # stock_svc = StockService(self.db)
        # stock_svc.consumir_stock(peca_id=peca.id, loja_id=os.loja_id, quantidade=quantidade)
        
        # 2. Adicionar peça à OS tirando um Snapshot do Preço de Venda
        nova_peca_os = self.repo.adicionar_peca_os(
            os_id=os.id, 
            peca_id=peca.id, 
            quantidade=quantidade, 
            preco_venda_unitario=peca.preco_venda
        )

        # Commit da transação ACID Única (Garante que se as peças forem adicionadas, o stock também baixa obrigatoriamente)
        self.db.commit()
        self.db.refresh(os)
        return nova_peca_os

    def iniciar_tempo(self, os_id: int, current_user: CurrentUserResponse):
        os = self.obter(os_id, current_user)
        rt = RegistoTempo(ordem_servico_id=os.id, inicio=datetime.now(timezone.utc))
        self.db.add(rt)
        self.db.commit()
        return rt

    # Implementações análogas podem ser seguidas para criar(...) e parar_tempo(...)
    # assegurando o save final da transação com self.db.commit().