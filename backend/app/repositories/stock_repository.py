from sqlalchemy.orm import Session, joinedload
from app.models.stock import StockLoja

class StockRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, peca_id: int, loja_id: int) -> StockLoja | None:
        return self.db.query(StockLoja).filter(
            StockLoja.peca_id == peca_id,
            StockLoja.loja_id == loja_id
        ).first()

    def get_or_create(self, peca_id: int, loja_id: int) -> StockLoja:
        stock = self.get(peca_id, loja_id)
        if not stock:
            stock = StockLoja(peca_id=peca_id, loja_id=loja_id, quantidade=0, limite_minimo=2)
            self.db.add(stock)
            self.db.flush()  # Deixa o commit final para ser gerido pelo Service
        return stock

    def list(self, loja_id: int | None, apenas_alertas: bool, skip: int, limit: int) -> tuple[list[StockLoja], int]:
        query = self.db.query(StockLoja).options(
            joinedload(StockLoja.peca),
            joinedload(StockLoja.loja)
        )
        
        if loja_id is not None:
            query = query.filter(StockLoja.loja_id == loja_id)
            
        if apenas_alertas:
            query = query.filter(StockLoja.quantidade <= StockLoja.limite_minimo)
            
        total = query.count()
        itens = query.offset(skip).limit(limit).all()
        return itens, total

    def get_disponivel(self, peca_id: int, loja_id: int) -> int:
        stock = self.get(peca_id, loja_id)
        return stock.quantidade if stock else 0

    def adicionar(self, peca_id: int, loja_id: int, quantidade: int) -> StockLoja:
        stock = self.get_or_create(peca_id, loja_id)
        stock.quantidade += quantidade
        return stock

    def atualizar_minimo(self, peca_id: int, loja_id: int, minimo: int) -> StockLoja:
        stock = self.get_or_create(peca_id, loja_id)
        stock.limite_minimo = minimo
        return stock

    def consumir(self, peca_id: int, loja_id: int, quantidade: int) -> StockLoja:
        stock = self.get_or_create(peca_id, loja_id)
        if stock.quantidade < quantidade:
            raise ValueError("Stock insuficiente")
        stock.quantidade -= quantidade
        return stock

    def transferir(self, peca_id: int, loja_origem_id: int, loja_destino_id: int, quantidade: int) -> tuple[StockLoja, StockLoja]:
        origem = self.consumir(peca_id, loja_origem_id, quantidade) # Reutiliza a lógica e o ValueError se falhar
        destino = self.adicionar(peca_id, loja_destino_id, quantidade)
        
        return origem, destino