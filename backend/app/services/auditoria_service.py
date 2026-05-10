from __future__ import annotations

from app.repositories.auditoria_repository import MockAuditoriaRepository, AuditoriaEvento
from app.schemas.auditoria import TipoEventoAuditoria, AuditoriaItemResponse
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import PaginatedResponse

_repo = MockAuditoriaRepository()


def registar(
    evento: TipoEventoAuditoria,
    descricao: str,
    ip_origem: str = "127.0.0.1",
    utilizador_id: int | None = None,
    utilizador_nome: str | None = None,
    loja_id: int | None = None,
    detalhe: dict | None = None,
) -> AuditoriaEvento:
    return _repo.registar(
        evento=evento,
        descricao=descricao,
        ip_origem=ip_origem,
        utilizador_id=utilizador_id,
        utilizador_nome=utilizador_nome,
        loja_id=loja_id,
        detalhe=detalhe,
    )


def listar(
    evento: str | None,
    utilizador_id: int | None,
    loja_id: int | None,
    data_inicio,
    data_fim,
    page: int,
    page_size: int,
    current_user: CurrentUserResponse,
) -> PaginatedResponse[AuditoriaItemResponse]:
    itens, total = _repo.list(
        loja_id=loja_id,
        evento=evento,
        utilizador_id=utilizador_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        current_user_perfil=current_user.perfil,
        current_user_loja_id=current_user.loja_id,
        page=page,
        page_size=page_size,
    )
    pages = max(1, -(-total // page_size))

    return PaginatedResponse[AuditoriaItemResponse](
        data=[AuditoriaItemResponse(**i.__dict__) for i in itens],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
