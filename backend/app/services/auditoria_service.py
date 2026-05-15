from __future__ import annotations

from app.repositories.auditoria_repository import AuditoriaRepository
from app.models.auditoria import Auditoria
from app.schemas.auditoria import TipoEventoAuditoria, AuditoriaItemResponse
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import PaginatedResponse
from app.schemas.utilizador import PerfilUtilizador

class AuditoriaService:
    def __init__(self, repo: AuditoriaRepository):
        self.repo = repo

    def registar(
        self,
        evento: TipoEventoAuditoria,
        descricao: str,
        ip_origem: str = "127.0.0.1",
        utilizador_id: int | None = None,
        utilizador_nome: str | None = None,
        loja_id: int | None = None,
        detalhe: dict | None = None,
    ) -> Auditoria:
        return self.repo.registar(
            evento=evento,
            descricao=descricao,
            ip_origem=ip_origem,
            utilizador_id=utilizador_id,
            utilizador_nome=utilizador_nome,
            loja_id=loja_id,
            detalhe=detalhe,
        )

    def listar(
        self,
        evento: str | None,
        utilizador_id: int | None,
        loja_id: int | None,
        data_inicio,
        data_fim,
        page: int,
        page_size: int,
        current_user: CurrentUserResponse,
    ) -> PaginatedResponse[AuditoriaItemResponse]:
        if current_user.perfil != PerfilUtilizador.ADMINISTRADOR:
            loja_id = current_user.loja_id

        itens, total = self.repo.listar(
            loja_id=loja_id,
            evento=evento,
            utilizador_id=utilizador_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            page=page,
            page_size=page_size,
        )
        pages = max(1, -(-total // page_size))

        def _build_response(item: Auditoria) -> AuditoriaItemResponse:
            # Mapeia dinamicamente o nome a partir da relação SQLAlchemy (se existir)
            nome_user = item.utilizador.nome if item.utilizador else None
            return AuditoriaItemResponse(
                id=item.id,
                evento=item.evento,
                descricao=item.descricao,
                utilizador_id=item.utilizador_id,
                utilizador_nome=nome_user,
                loja_id=item.loja_id,
                ip_origem=item.ip_origem,
                timestamp=item.timestamp,
                detalhe=item.detalhe
            )

        return PaginatedResponse[AuditoriaItemResponse](
            data=[_build_response(i) for i in itens],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )
