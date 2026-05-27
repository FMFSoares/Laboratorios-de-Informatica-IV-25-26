from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import CurrentUserResponse
from app.auth.dependencies import get_current_user, require_roles
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.common import DataResponse
from app.schemas.servico import ServicoCreate, ServicoUpdate, ServicoResponse
from app.services.servico_service import ServicoService

router = APIRouter(prefix="/servicos", tags=["serviços"])


def get_service(db: Session = Depends(get_db)) -> ServicoService:
    return ServicoService(db)


@router.get("/{servico_id}", response_model=DataResponse[ServicoResponse])
def obter_servico(
    servico_id: int,
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: ServicoService = Depends(get_service),
):
    return DataResponse[ServicoResponse](data=service.obter(servico_id))


@router.get("/", response_model=DataResponse[list[ServicoResponse]])
def listar_servicos(
    apenas_ativos: bool = Query(False),
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: ServicoService = Depends(get_service),
):
    return DataResponse[list[ServicoResponse]](data=service.listar(apenas_ativos))


@router.post("/", response_model=DataResponse[ServicoResponse], status_code=201)
def criar_servico(
    body: ServicoCreate,
    current_user: CurrentUserResponse = Depends(
        require_roles(PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA)
    ),
    service: ServicoService = Depends(get_service),
):
    return DataResponse[ServicoResponse](data=service.criar(body, current_user))


@router.patch("/{servico_id}", response_model=DataResponse[ServicoResponse])
def atualizar_servico(
    servico_id: int,
    body: ServicoUpdate,
    current_user: CurrentUserResponse = Depends(
        require_roles(PerfilUtilizador.ADMINISTRADOR, PerfilUtilizador.GERENTE_LOJA)
    ),
    service: ServicoService = Depends(get_service),
):
    return DataResponse[ServicoResponse](data=service.atualizar(servico_id, body, current_user))
