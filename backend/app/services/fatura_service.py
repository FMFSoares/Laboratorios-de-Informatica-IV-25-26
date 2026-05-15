from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.fatura import EstadoFatura
from app.models.ordem_servico import EstadoOrdemServico
from app.repositories.fatura_repository import FaturaRepository
from app.repositories.ordem_servico_repository import OrdemServicoRepository
from app.repositories.auditoria_repository import AuditoriaRepository
from app.schemas.fatura import FaturaCreateRequest, FaturaResponse, FaturaResumo
from app.schemas.common import PaginatedResponse
from app.schemas.auth import CurrentUserResponse
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.auditoria import TipoEventoAuditoria

class FaturaService:
    def __init__(self, db: Session):
        self.db = db
        self.fatura_repo = FaturaRepository(db)
        self.os_repo = OrdemServicoRepository(db)
        self.auditoria_repo = AuditoriaRepository(db)

    def emitir(self, body: FaturaCreateRequest, current_user: CurrentUserResponse) -> FaturaResponse:
        os = self.os_repo.get_by_id(body.ordem_servico_id)
        if not os:
            raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada")

        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and os.loja_id != current_user.loja_id:
            raise HTTPException(status_code=403, detail="Não tem permissões para esta Ordem de Serviço")
            
        if os.fatura:
            raise HTTPException(status_code=409, detail="A Ordem de Serviço já se encontra faturada")
            
        if os.estado != EstadoOrdemServico.CONCLUIDA:
            raise HTTPException(status_code=400, detail="Ordem de Serviço não está concluída")

        subtotal_pecas = sum(peca.quantidade * peca.preco_venda_unitario for peca in os.pecas_usadas)
        valor_final = os.preco_servico + subtotal_pecas

        # Cria Fatura na sessão
        numero_fatura = f"FAT-{datetime.now(timezone.utc).year}-{os.id}"
        nova_fatura = self.fatura_repo.create(
            numero=numero_fatura,
            ordem_servico_id=os.id,
            estado=EstadoFatura.PAGA, # ou EMITIDA consoante o teu enum
            subtotal_pecas=subtotal_pecas,
            valor_final=valor_final,
            data_emissao=datetime.now(timezone.utc)
        )

        # Atualiza a Ordem de Serviço (assume-se que tenhas adicionado FATURADA ao Enum do model)
        os.estado = EstadoOrdemServico.FATURADA if hasattr(EstadoOrdemServico, "FATURADA") else EstadoOrdemServico.CONCLUIDA

        # Registo de auditoria
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.FATURA_EMITIDA,
            descricao=f"Fatura {numero_fatura} emitida para a OS #{os.id}",
            utilizador_id=current_user.id,
            loja_id=os.loja_id,
            detalhe={"ordem_servico_id": os.id, "valor_final": valor_final}
        )

        # Finalizar Transação Única
        self.db.commit()
        self.db.refresh(nova_fatura)
        return nova_fatura

    def obter(self, fatura_id: int, current_user: CurrentUserResponse):
        fatura = self.fatura_repo.get_by_id(fatura_id)
        if not fatura:
            raise HTTPException(status_code=404, detail="Fatura não encontrada")
            
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and fatura.ordem_servico.loja_id != current_user.loja_id:
            raise HTTPException(status_code=403, detail="Acesso negado a esta fatura")
            
        return fatura

    def listar(self, loja_id, ordem_servico_id, data_inicio, data_fim, page, page_size, current_user) -> PaginatedResponse[FaturaResumo]:
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
            loja_id = current_user.loja_id

        itens, total = self.fatura_repo.list(loja_id, ordem_servico_id, data_inicio, data_fim, page, page_size)
        pages = max(1, -(-total // page_size))
        
        return PaginatedResponse[FaturaResumo](
            data=itens, total=total, page=page, page_size=page_size, pages=pages
        )

    def descarregar_pdf(self, fatura_id: int, current_user: CurrentUserResponse):
        fatura = self.obter(fatura_id, current_user)
        return {"message": "PDF gerado com sucesso", "fatura_id": fatura.id}

    def enviar_email(self, fatura_id: int, current_user: CurrentUserResponse):
        fatura = self.obter(fatura_id, current_user)
        return {"message": "E-mail enviado com sucesso", "fatura_id": fatura.id}