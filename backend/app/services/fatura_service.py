from datetime import datetime, timezone
import io
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
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
            raise HTTPException(status_code=409, detail={"detail": "A Ordem de Serviço já se encontra faturada.", "code": "ORDER_ALREADY_INVOICED"})

        if os.estado != EstadoOrdemServico.CONCLUIDA:
            raise HTTPException(status_code=400, detail={"detail": "Ordem de Serviço não está concluída.", "code": "ORDER_NOT_CONCLUDED"})

        subtotal_pecas = sum(peca.quantidade * peca.preco_venda_unitario for peca in os.pecas_aplicadas)

        # Calculate discount
        desconto_tipo = body.desconto_tipo.value if body.desconto_tipo else None
        desconto_valor = body.desconto_valor
        if body.desconto_tipo is None or body.desconto_valor == 0.0:
            valor_desconto = 0.0
        elif body.desconto_tipo.value == "PERCENTUAL":
            base = os.preco_servico + subtotal_pecas
            valor_desconto = round(base * body.desconto_valor / 100, 2)
        else:  # FIXO
            valor_desconto = body.desconto_valor

        valor_final = os.preco_servico + subtotal_pecas - valor_desconto

        # Cria Fatura na sessão com numero=None; flush para obter o ID auto-incrementado
        nova_fatura = self.fatura_repo.create(
            numero=None,
            ordem_servico_id=os.id,
            estado=EstadoFatura.EMITIDA,
            subtotal_pecas=subtotal_pecas,
            valor_final=valor_final,
            data_emissao=datetime.now(timezone.utc),
            desconto_tipo=desconto_tipo,
            desconto_valor=desconto_valor,
            valor_desconto=valor_desconto,
        )

        self.db.flush()  # Obtém o ID sem fazer commit
        year = datetime.now(timezone.utc).year
        nova_fatura.numero = f"FAT-{year}-{nova_fatura.id:04d}"
        numero_fatura = nova_fatura.numero

        os.estado = EstadoOrdemServico.FATURADA

        # Registo de auditoria
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.FATURA_EMITIDA,
            descricao=f"Fatura {numero_fatura} emitida para a OS #{os.id}",
            utilizador_id=current_user.id,
            loja_id=os.loja_id,
            detalhe={"ordem_servico_id": os.id, "valor_final": valor_final}
        )

        self.db.commit()
        fatura_completa = self.fatura_repo.get_by_id(nova_fatura.id)
        response = self._build_fatura_response(fatura_completa)

        try:
            if response.cliente.email:
                from app.utils.pdf import gerar_pdf_fatura
                from app.utils.email import enviar_fatura_email
                pdf_bytes = gerar_pdf_fatura(response)
                enviar_fatura_email(
                    cliente_email=response.cliente.email,
                    cliente_nome=response.cliente.nome,
                    fatura_numero=response.numero,
                    loja_nome=response.loja.nome,
                    loja_telefone=response.loja.telefone,
                    pdf_bytes=pdf_bytes,
                )
        except Exception:
            pass

        return response

    def _build_fatura_response(self, fatura) -> FaturaResponse:
        from app.schemas.fatura import (
            FaturaClienteInfo, FaturaTrotineteInfo, FaturaServicoInfo,
            FaturaPecaAplicada, FaturaLojaInfo,
        )
        os = fatura.ordem_servico
        pecas = [
            FaturaPecaAplicada(
                peca_referencia=p.peca.referencia,
                peca_nome=p.peca.nome,
                quantidade=p.quantidade,
                preco_venda_unitario=p.preco_venda_unitario,
                subtotal=p.quantidade * p.preco_venda_unitario,
            )
            for p in os.pecas_aplicadas
        ]
        return FaturaResponse(
            id=fatura.id,
            numero=fatura.numero,
            ordem_servico_id=fatura.ordem_servico_id,
            data_emissao=fatura.data_emissao,
            estado=fatura.estado,
            cliente=FaturaClienteInfo(
                id=os.cliente.id,
                nome=os.cliente.nome,
                nif=os.cliente.nif,
                morada=os.cliente.morada,
                email=os.cliente.email,
            ),
            trotinete=FaturaTrotineteInfo(
                marca=os.trotinete.marca,
                modelo=os.trotinete.modelo,
                numero_serie=os.trotinete.numero_serie,
            ),
            servico=FaturaServicoInfo(
                descricao=os.descricao_problema,
                preco_servico=os.preco_servico,
            ),
            pecas_aplicadas=pecas,
            subtotal_pecas=fatura.subtotal_pecas,
            desconto_tipo=fatura.desconto_tipo,
            desconto_valor=fatura.desconto_valor,
            valor_desconto=fatura.valor_desconto,
            valor_final=fatura.valor_final,
            loja=FaturaLojaInfo(
                nome=os.loja.nome,
                morada=os.loja.morada,
                telefone=os.loja.telefone,
            ),
        )

    def obter(self, fatura_id: int, current_user: CurrentUserResponse) -> FaturaResponse:
        fatura = self.fatura_repo.get_by_id(fatura_id)
        if not fatura:
            raise HTTPException(status_code=404, detail="Fatura não encontrada")

        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and fatura.ordem_servico.loja_id != current_user.loja_id:
            raise HTTPException(status_code=403, detail="Acesso negado a esta fatura")

        return self._build_fatura_response(fatura)

    def listar(self, loja_id, ordem_servico_id, data_inicio, data_fim, page, page_size, current_user) -> PaginatedResponse[FaturaResumo]:
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
            loja_id = current_user.loja_id

        itens, total = self.fatura_repo.list(loja_id, ordem_servico_id, data_inicio, data_fim, page, page_size)
        pages = max(1, -(-total // page_size))

        resumos = [
            FaturaResumo(
                id=f.id,
                numero=f.numero,
                ordem_servico_id=f.ordem_servico_id,
                cliente_nome=f.ordem_servico.cliente.nome,
                cliente_nif=f.ordem_servico.cliente.nif,
                valor_final=f.valor_final,
                data_emissao=f.data_emissao,
                estado=f.estado,
            )
            for f in itens
        ]

        return PaginatedResponse[FaturaResumo](
            data=resumos, total=total, page=page, page_size=page_size, pages=pages
        )

    def descarregar_pdf(self, fatura_id: int, current_user: CurrentUserResponse) -> StreamingResponse:
        from app.utils.pdf import gerar_pdf_fatura
        fatura = self.obter(fatura_id, current_user)
        pdf_bytes = gerar_pdf_fatura(fatura)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{fatura.numero}.pdf"'},
        )

    def enviar_email(self, fatura_id: int, current_user: CurrentUserResponse):
        from app.utils.email import enviar_fatura_email
        from app.utils.pdf import gerar_pdf_fatura
        fatura = self.obter(fatura_id, current_user)
        if not fatura.cliente.email:
            raise HTTPException(status_code=400, detail="O cliente não tem email registado.")
        pdf_bytes = gerar_pdf_fatura(fatura)
        enviar_fatura_email(
            cliente_email=fatura.cliente.email,
            cliente_nome=fatura.cliente.nome,
            fatura_numero=fatura.numero,
            loja_nome=fatura.loja.nome,
            loja_telefone=fatura.loja.telefone,
            pdf_bytes=pdf_bytes,
        )
        return {"message": "E-mail enviado com sucesso.", "fatura_id": fatura.id}