from sqlalchemy.orm import Session

from app.models.servico import Servico


class ServicoRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, apenas_ativos: bool = False) -> list[Servico]:
        q = self.db.query(Servico)
        if apenas_ativos:
            q = q.filter(Servico.ativo == True)
        return q.order_by(Servico.nome).all()

    def get_by_id(self, servico_id: int) -> Servico | None:
        return self.db.query(Servico).filter(Servico.id == servico_id).first()

    def create(self, nome: str, preco_base: float, ativo: bool = True) -> Servico:
        s = Servico(nome=nome, preco_base=preco_base, ativo=ativo)
        self.db.add(s)
        return s

    def update(self, servico: Servico, **kwargs) -> Servico:
        for k, v in kwargs.items():
            if v is not None:
                setattr(servico, k, v)
        return servico
