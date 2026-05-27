from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.loja import LojaResumo
from app.schemas.peca import PecaResumo


class EstadoPedidoTransferencia(str, Enum):
    PENDENTE  = "PENDENTE"
    ACEITE    = "ACEITE"
    CONCLUIDA = "CONCLUIDA"
    RECUSADO  = "RECUSADO"
    CANCELADO = "CANCELADO"


class EstadoPedidoPeca(str, Enum):
    PENDENTE  = "PENDENTE"
    APROVADO  = "APROVADO"
    RECUSADO  = "RECUSADO"


# ── Transfer request ──────────────────────────────────────────────────────────

class PedidoTransferenciaCreate(BaseModel):
    loja_origem_id: int = Field(..., gt=0)
    peca_id: int        = Field(..., gt=0)
    quantidade: int     = Field(..., gt=0)
    observacoes: str | None = None


class PedidoTransferenciaResponder(BaseModel):
    aceitar: bool
    observacoes: str | None = None


class UtilizadorResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str


class PedidoTransferenciaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    estado: EstadoPedidoTransferencia
    loja_origem: LojaResumo
    loja_destino: LojaResumo
    gerente_origem: UtilizadorResumo
    gerente_destino: UtilizadorResumo
    peca: PecaResumo
    quantidade: int
    data_pedido: datetime
    data_resposta: datetime | None
    data_recepcao: datetime | None
    data_assinatura_origem: datetime | None
    data_assinatura_destino: datetime | None
    observacoes_pedido: str | None
    observacoes_resposta: str | None


# ── Part request (mechanic → gerente) ────────────────────────────────────────

class PedidoPecaCreate(BaseModel):
    ordem_servico_id: int = Field(..., gt=0)
    peca_id: int          = Field(..., gt=0)
    quantidade: int       = Field(..., gt=0)
    observacoes: str | None = None


class PedidoPecaResponder(BaseModel):
    aprovar: bool
    observacoes: str | None = None


class OSResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero: str


class PedidoPecaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    estado: EstadoPedidoPeca
    peca: PecaResumo
    ordem_servico: OSResumo
    mecanico: UtilizadorResumo
    loja: LojaResumo
    quantidade: int
    data_pedido: datetime
    data_resposta: datetime | None
    observacoes: str | None
