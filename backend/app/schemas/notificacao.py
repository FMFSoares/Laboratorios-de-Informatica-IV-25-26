from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class TipoNotificacao(str, Enum):
    PEDIDO_PECA             = "PEDIDO_PECA"
    PEDIDO_TRANSFERENCIA    = "PEDIDO_TRANSFERENCIA"
    TRANSFERENCIA_ACEITE    = "TRANSFERENCIA_ACEITE"
    TRANSFERENCIA_RECUSADA  = "TRANSFERENCIA_RECUSADA"
    TRANSFERENCIA_CONCLUIDA = "TRANSFERENCIA_CONCLUIDA"
    PECA_APROVADA           = "PECA_APROVADA"
    PECA_RECUSADA           = "PECA_RECUSADA"


class NotificacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoNotificacao
    titulo: str
    mensagem: str
    lida: bool
    data_criacao: datetime
    referencia_id: int | None
    referencia_tipo: str | None
