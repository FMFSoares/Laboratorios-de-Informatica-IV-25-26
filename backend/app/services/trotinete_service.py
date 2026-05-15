from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.trotinete_repository import TrotineteRepository
from app.schemas.trotinete import TrotineteCreate, TrotineteResponse, TrotineteDetalheResponse, ClienteResumoEmTrotinete
from app.schemas.auth import CurrentUserResponse
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.common import DataResponse, PaginatedResponse

# Import local cruzado para validar o cliente
from app.services import cliente_service

class TrotineteService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TrotineteRepository(db)

    def _find(self, trotinete_id: int):
        trotinete = self.repo.get_by_id(trotinete_id)
        if not trotinete:
            raise HTTPException(status_code=404, detail="Trotinete não encontrada.")
        return trotinete

    def get_por_cliente(self, cliente_id: int):
        itens = self.repo.list_by_cliente(cliente_id)
        data = []
        for t in itens:
            t_dict = {k: v for k, v in t.__dict__.items() if not k.startswith("_")}
            data.append(TrotineteResponse(**t_dict))
        return data

    def listar(
        self,
        cliente_id: int | None,
        numero_serie: str | None,
        page: int,
        page_size: int,
        current_user: CurrentUserResponse
    ) -> PaginatedResponse[TrotineteResponse]:
        loja_id = current_user.loja_id if current_user.perfil != PerfilUtilizador.ADMINISTRADOR else None
        skip = (page - 1) * page_size
        itens, total = self.repo.list(loja_id, cliente_id, numero_serie, skip, page_size)
        pages = max(1, -(-total // page_size))

        data = []
        for t in itens:
            t_dict = {k: v for k, v in t.__dict__.items() if not k.startswith("_")}
            data.append(TrotineteResponse(**t_dict))

        return PaginatedResponse[TrotineteResponse](
            data=data, total=total, page=page, page_size=page_size, pages=pages
        )

    def criar(self, body: TrotineteCreate, current_user: CurrentUserResponse) -> DataResponse[TrotineteResponse]:
        cliente = cliente_service._find(self.db, body.cliente_id)
        
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and cliente.loja_id != current_user.loja_id:
            raise HTTPException(status_code=403, detail="Acesso negado a este cliente.")

        if self.repo.exists_numero_serie(body.numero_serie):
            raise HTTPException(status_code=409, detail="Número de série já registado.")

        nova = self.repo.create(**body.model_dump())
        t_dict = {k: v for k, v in nova.__dict__.items() if not k.startswith("_")}
        
        return DataResponse[TrotineteResponse](data=TrotineteResponse(**t_dict), message="Trotinete registada com sucesso.")

    def obter(self, trotinete_id: int, current_user: CurrentUserResponse) -> DataResponse[TrotineteDetalheResponse]:
        trotinete = self._find(trotinete_id)
        cliente = cliente_service._find(self.db, trotinete.cliente_id)
        
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and cliente.loja_id != current_user.loja_id:
            raise HTTPException(status_code=403, detail="Acesso negado a esta trotinete.")

        total_ordens = self.repo.count_by_trotinete(trotinete_id)
        
        t_dict = {k: v for k, v in trotinete.__dict__.items() if not k.startswith("_")}
        c_dict = {k: v for k, v in cliente.__dict__.items() if not k.startswith("_")}
        detalhe = TrotineteDetalheResponse(**t_dict, cliente=ClienteResumoEmTrotinete(**c_dict), total_ordens=total_ordens)
        
        return DataResponse[TrotineteDetalheResponse](data=detalhe)