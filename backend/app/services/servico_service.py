from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories.auditoria_repository import AuditoriaRepository
from app.repositories.servico_repository import ServicoRepository
from app.schemas.auditoria import TipoEventoAuditoria
from app.schemas.servico import ServicoCreate, ServicoUpdate, ServicoResponse
from app.schemas.auth import CurrentUserResponse


class ServicoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ServicoRepository(db)
        self.auditoria_repo = AuditoriaRepository(db)

    def obter(self, servico_id: int) -> ServicoResponse:
        s = self.repo.get_by_id(servico_id)
        if not s:
            raise HTTPException(status_code=404, detail="Serviço não encontrado.")
        return ServicoResponse.model_validate(s)

    def listar(self, apenas_ativos: bool = False) -> list[ServicoResponse]:
        return [ServicoResponse.model_validate(s) for s in self.repo.list(apenas_ativos)]

    def criar(self, body: ServicoCreate, current_user: CurrentUserResponse) -> ServicoResponse:
        s = self.repo.create(nome=body.nome, preco_base=body.preco_base, ativo=body.ativo)
        self.db.flush()
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.SERVICO_CRIADO,
            descricao=f"Serviço '{body.nome}' criado no catálogo (preço base: {body.preco_base} €)",
            utilizador_id=current_user.id,
            detalhe={"nome": body.nome, "preco_base": body.preco_base, "ativo": body.ativo},
        )
        self.db.commit()
        self.db.refresh(s)
        return ServicoResponse.model_validate(s)

    def atualizar(self, servico_id: int, body: ServicoUpdate, current_user: CurrentUserResponse) -> ServicoResponse:
        s = self.repo.get_by_id(servico_id)
        if not s:
            raise HTTPException(status_code=404, detail="Serviço não encontrado.")
        updates = {k: v for k, v in body.model_dump().items() if v is not None}
        self.repo.update(s, **updates)
        self.auditoria_repo.registar(
            evento=TipoEventoAuditoria.SERVICO_ATUALIZADO,
            descricao=f"Serviço '{s.nome}' atualizado",
            utilizador_id=current_user.id,
            detalhe={"servico_id": servico_id, "campos": list(updates.keys())},
        )
        self.db.commit()
        self.db.refresh(s)
        return ServicoResponse.model_validate(s)
