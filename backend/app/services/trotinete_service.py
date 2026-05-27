from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.auditoria_repository import AuditoriaRepository
from app.repositories.trotinete_repository import TrotineteRepository
from app.schemas.trotinete import TrotineteCreate, TrotineteResponse, TrotineteDetalheResponse, ClienteResumoEmTrotinete
from app.schemas.auth import CurrentUserResponse
from app.schemas.auditoria import TipoEventoAuditoria
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.common import DataResponse, PaginatedResponse

# Import local cruzado para validar o cliente
from app.repositories.cliente_repository import ClienteRepository

class TrotineteService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TrotineteRepository(db)
        self.auditoria_repo = AuditoriaRepository(db)

    def _find(self, trotinete_id: int):
        trotinete = self.repo.get_by_id(trotinete_id)
        if not trotinete:
            raise HTTPException(status_code=404, detail="Trotinete não encontrada.")
        return trotinete

    def get_por_cliente(self, cliente_id: int):
        return [TrotineteResponse.model_validate(t) for t in self.repo.list_by_cliente(cliente_id)]

    def listar(
        self,
        cliente_id: int | None,
        query_str: str | None,
        page: int,
        page_size: int,
        current_user: CurrentUserResponse
    ) -> PaginatedResponse[TrotineteResponse]:
        loja_id = current_user.loja_id if current_user.perfil != PerfilUtilizador.ADMINISTRADOR else None
        skip = (page - 1) * page_size
        itens, total = self.repo.list(loja_id, cliente_id, query_str, skip, page_size)
        pages = max(1, -(-total // page_size))

        return PaginatedResponse[TrotineteResponse](
            data=[TrotineteResponse.model_validate(t) for t in itens],
            total=total, page=page, page_size=page_size, pages=pages
        )

    def _get_cliente(self, cliente_id: int):
        return ClienteRepository(self.db).get_by_id(cliente_id)

    def criar(self, body: TrotineteCreate, current_user: CurrentUserResponse) -> DataResponse[TrotineteResponse]:
        cliente = self._get_cliente(body.cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")

        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and cliente.loja_id != current_user.loja_id:
            raise HTTPException(status_code=403, detail="Acesso negado a este cliente.")

        if self.repo.exists_numero_serie(body.numero_serie):
            raise HTTPException(status_code=409, detail="Número de série já registado.")

        nova = self.repo.create(**body.model_dump())
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.TROTINETE_REGISTADA,
            descricao=f"Trotinete '{body.numero_serie}' registada para o cliente #{body.cliente_id}",
            utilizador_id=current_user.id,
            loja_id=cliente.loja_id,
            detalhe={"numero_serie": body.numero_serie, "marca": body.marca, "modelo": body.modelo, "cliente_id": body.cliente_id},
        )
        self.db.commit()
        # Reload with client eagerly loaded so the model_validator can read cliente.nome
        nova = self.repo.get_by_id(nova.id)
        return DataResponse[TrotineteResponse](data=TrotineteResponse.model_validate(nova), message="Trotinete registada com sucesso.")

    def obter(self, trotinete_id: int, current_user: CurrentUserResponse) -> DataResponse[TrotineteDetalheResponse]:
        trotinete = self._find(trotinete_id)
        cliente = self._get_cliente(trotinete.cliente_id)
        
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR and cliente.loja_id != current_user.loja_id:
            raise HTTPException(status_code=403, detail="Acesso negado a esta trotinete.")

        total_ordens = self.repo.count_by_trotinete(trotinete_id)
        detalhe = TrotineteDetalheResponse(
            **TrotineteResponse.model_validate(trotinete).model_dump(),
            cliente=ClienteResumoEmTrotinete.model_validate(cliente),
            total_ordens=total_ordens,
        )
        return DataResponse[TrotineteDetalheResponse](data=detalhe)

    def apagar(self, trotinete_id: int, current_user: CurrentUserResponse) -> None:
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
            raise HTTPException(status_code=403, detail="Apenas administradores podem eliminar trotinetes.")
        trotinete = self._find(trotinete_id)
        self.db.delete(trotinete)
        self.db.commit()