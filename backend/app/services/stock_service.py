from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.auditoria_repository import AuditoriaRepository
from app.repositories.stock_repository import StockRepository
from app.repositories.loja_repository import LojaRepository
from app.repositories.peca_repository import PecaRepository
from app.models.peca import Peca
from app.schemas.stock import StockItemResponse, StockEntradaRequest, StockEntradaResponse, StockTransferenciaRequest, StockTransferenciaResponse
from app.schemas.auth import CurrentUserResponse
from app.schemas.auditoria import TipoEventoAuditoria
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.common import PaginatedResponse, DataResponse

class StockService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = StockRepository(db)
        self.loja_repo = LojaRepository(db)
        self.peca_repo = PecaRepository(db)
        self.auditoria_repo = AuditoriaRepository(db)

    def _to_item_response(self, s) -> StockItemResponse:
        # Aproveita os relacionamentos SQLAlchemy (joinedload do repository) evitando N+1 queries.
        return StockItemResponse(
            peca_id=s.peca_id,
            peca_referencia=s.peca.referencia if s.peca else "",
            peca_nome=s.peca.nome if s.peca else "",
            loja_id=s.loja_id,
            loja_nome=s.loja.nome if s.loja else "",
            quantidade=s.quantidade,
            limite_minimo=s.limite_minimo,
            alerta=s.quantidade <= s.limite_minimo
        )

    def consumir_stock(self, peca_id: int, loja_id: int, quantidade: int):
        try:
            self.repo.consumir(peca_id, loja_id, quantidade)
            self.db.commit()
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_stock_disponivel(self, peca_id: int, loja_id: int) -> int:
        return self.repo.get_disponivel(peca_id, loja_id)

    def listar(
        self, loja_id: int | None, apenas_alertas: bool, page: int, page_size: int, current_user: CurrentUserResponse, peca_id: int | None = None
    ) -> PaginatedResponse[StockItemResponse]:
        if current_user.perfil not in (PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA):
            loja_id = current_user.loja_id

        skip = (page - 1) * page_size
        itens, total = self.repo.list(loja_id, apenas_alertas, skip, page_size, peca_id=peca_id)
        pages = max(1, -(-total // page_size))

        data = [self._to_item_response(i) for i in itens]

        return PaginatedResponse[StockItemResponse](
            data=data, total=total, page=page, page_size=page_size, pages=pages
        )

    def atualizar_minimo(self, peca_id: int, loja_id: int, minimo: int, current_user: CurrentUserResponse):
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and current_user.loja_id != loja_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado à loja")

        self.repo.atualizar_minimo(peca_id, loja_id, minimo)
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.STOCK_MINIMO_ALTERADO,
            descricao=f"Stock mínimo da peça #{peca_id} na loja #{loja_id} definido para {minimo}",
            utilizador_id=current_user.id,
            loja_id=loja_id,
            detalhe={"peca_id": peca_id, "loja_id": loja_id, "novo_minimo": minimo},
        )
        self.db.commit()

    def entrada(self, body: StockEntradaRequest, current_user: CurrentUserResponse) -> DataResponse[StockEntradaResponse]:
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and body.loja_id != current_user.loja_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado à loja")

        if not self.loja_repo.get_by_id(body.loja_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loja não encontrada")
            
        if not self.peca_repo.get_by_id(body.peca_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peça não encontrada")

        stock_antes = self.repo.get(body.peca_id, body.loja_id)
        quantidade_anterior = stock_antes.quantidade if stock_antes else 0

        peca = self.db.query(Peca).filter(Peca.id == body.peca_id).first()
        peca_nome = peca.nome if peca else ""

        stock = self.repo.adicionar(body.peca_id, body.loja_id, body.quantidade)
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.STOCK_ENTRADA,
            descricao=f"Entrada de {body.quantidade}x '{peca_nome}' na loja #{body.loja_id}",
            utilizador_id=current_user.id,
            loja_id=body.loja_id,
            detalhe={"peca_id": body.peca_id, "peca_nome": peca_nome, "loja_id": body.loja_id, "quantidade": body.quantidade, "quantidade_anterior": quantidade_anterior},
        )
        self.db.commit()
        self.db.refresh(stock)

        return DataResponse[StockEntradaResponse](
            data=StockEntradaResponse(
                peca_id=stock.peca_id,
                peca_nome=peca_nome,
                loja_id=stock.loja_id,
                quantidade_anterior=quantidade_anterior,
                quantidade_adicionada=body.quantidade,
                quantidade_atual=stock.quantidade,
                alerta=stock.quantidade <= stock.limite_minimo,
            ),
            message="Entrada de stock registada com sucesso."
        )

    def transferencia(self, body: StockTransferenciaRequest, current_user: CurrentUserResponse) -> DataResponse[StockTransferenciaResponse]:
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and body.loja_origem_id != current_user.loja_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado à loja de origem")

        if not self.loja_repo.get_by_id(body.loja_origem_id) or not self.loja_repo.get_by_id(body.loja_destino_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loja de origem ou destino não encontrada")

        if not self.peca_repo.get_by_id(body.peca_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peça não encontrada")

        peca = self.db.query(Peca).filter(Peca.id == body.peca_id).first()
        peca_nome = peca.nome if peca else ""

        try:
            origem, destino = self.repo.transferir(body.peca_id, body.loja_origem_id, body.loja_destino_id, body.quantidade)
            self.auditoria_repo.registar(
                evento=TipoEventoAuditoria.STOCK_TRANSFERENCIA,
                descricao=f"Transferência de {body.quantidade}x '{peca_nome}' da loja #{body.loja_origem_id} para loja #{body.loja_destino_id}",
                utilizador_id=current_user.id,
                loja_id=body.loja_origem_id,
                detalhe={"peca_id": body.peca_id, "peca_nome": peca_nome, "loja_origem_id": body.loja_origem_id, "loja_destino_id": body.loja_destino_id, "quantidade": body.quantidade},
            )
            self.db.commit()
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        self.db.refresh(origem)
        self.db.refresh(destino)

        return DataResponse[StockTransferenciaResponse](
            data=StockTransferenciaResponse(
                peca_id=origem.peca_id,
                peca_nome=peca_nome,
                loja_origem_id=origem.loja_id,
                loja_destino_id=destino.loja_id,
                quantidade_transferida=body.quantidade,
                stock_origem_apos=origem.quantidade,
                stock_destino_apos=destino.quantidade,
            ),
            message="Transferência registada com sucesso."
        )