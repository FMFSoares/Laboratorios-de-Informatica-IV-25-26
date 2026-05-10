from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import ClassVar

from app.schemas.auditoria import TipoEventoAuditoria as E


@dataclass
class AuditoriaEvento:
    id: int
    evento: E
    descricao: str
    ip_origem: str
    timestamp: datetime
    utilizador_id: int | None = None
    utilizador_nome: str | None = None
    loja_id: int | None = None
    detalhe: dict = field(default_factory=dict)


class MockAuditoriaRepository:
    _data: ClassVar[list[AuditoriaEvento]] = [
        AuditoriaEvento(
            id=1,
            evento=E.LOGIN_SUCESSO,
            descricao="Login efetuado com sucesso.",
            utilizador_id=3,
            utilizador_nome="Ana Rececionista",
            loja_id=1,
            ip_origem="192.168.1.10",
            timestamp=datetime(2026, 4, 28, 9, 0, tzinfo=timezone.utc),
            detalhe={"email": "ana.lisboa@dlmcare.pt"},
        ),
        AuditoriaEvento(
            id=2,
            evento=E.OS_ESTADO_ALTERADO,
            descricao="OS #1 alterada de PENDENTE para EM_DIAGNOSTICO.",
            utilizador_id=4,
            utilizador_nome="João Mecânico",
            loja_id=1,
            ip_origem="192.168.1.11",
            timestamp=datetime(2026, 4, 28, 10, 0, tzinfo=timezone.utc),
            detalhe={"ordem_servico_id": 1, "estado_anterior": "PENDENTE", "estado_novo": "EM_DIAGNOSTICO"},
        ),
        AuditoriaEvento(
            id=3,
            evento=E.STOCK_ENTRADA,
            descricao="Entrada de stock: 10 unidades de PEC-BAT-001 na loja 1.",
            utilizador_id=1,
            utilizador_nome="Admin DLMCare",
            loja_id=1,
            ip_origem="192.168.1.1",
            timestamp=datetime(2026, 4, 28, 11, 0, tzinfo=timezone.utc),
            detalhe={"peca_id": 1, "loja_id": 1, "quantidade": 10},
        ),
        AuditoriaEvento(
            id=4,
            evento=E.STOCK_TRANSFERENCIA,
            descricao="Transferência de 2 unidades de PEC-BAT-001 da loja 1 para loja 2.",
            utilizador_id=1,
            utilizador_nome="Admin DLMCare",
            loja_id=1,
            ip_origem="192.168.1.1",
            timestamp=datetime(2026, 4, 28, 12, 0, tzinfo=timezone.utc),
            detalhe={"peca_id": 1, "loja_origem_id": 1, "loja_destino_id": 2, "quantidade": 2},
        ),
        AuditoriaEvento(
            id=5,
            evento=E.FATURA_EMITIDA,
            descricao="Fatura FAT-2026-0001 emitida para OS #2.",
            utilizador_id=3,
            utilizador_nome="Ana Rececionista",
            loja_id=1,
            ip_origem="192.168.1.10",
            timestamp=datetime(2026, 4, 28, 17, 0, tzinfo=timezone.utc),
            detalhe={"fatura_id": 1, "ordem_servico_id": 2, "valor_final": 33.90},
        ),
        AuditoriaEvento(
            id=6,
            evento=E.ACESSO_NEGADO,
            descricao="Acesso negado: perfil MECANICO tentou aceder a POST /clientes.",
            utilizador_id=4,
            utilizador_nome="João Mecânico",
            loja_id=1,
            ip_origem="192.168.1.11",
            timestamp=datetime(2026, 4, 28, 14, 30, tzinfo=timezone.utc),
            detalhe={"endpoint": "POST /api/v1/clientes", "perfil": "MECANICO"},
        ),
        AuditoriaEvento(
            id=7,
            evento=E.LOGIN_FALHA,
            descricao="Tentativa de login falhada para o email desconhecido@dlmcare.pt.",
            ip_origem="10.0.0.99",
            timestamp=datetime(2026, 4, 28, 8, 55, tzinfo=timezone.utc),
            detalhe={"email": "desconhecido@dlmcare.pt"},
        ),
    ]
    _next_id: ClassVar[int] = 8

    def registar(
        self,
        evento: E,
        descricao: str,
        ip_origem: str,
        utilizador_id: int | None = None,
        utilizador_nome: str | None = None,
        loja_id: int | None = None,
        detalhe: dict | None = None,
    ) -> AuditoriaEvento:
        novo = AuditoriaEvento(
            id=self._next_id,
            evento=evento,
            descricao=descricao,
            utilizador_id=utilizador_id,
            utilizador_nome=utilizador_nome,
            loja_id=loja_id,
            ip_origem=ip_origem,
            timestamp=datetime.now(timezone.utc),
            detalhe=detalhe or {},
        )
        self._data.append(novo)
        type(self)._next_id += 1
        return novo

    def list(
        self,
        loja_id: int | None,
        evento: str | None,
        utilizador_id: int | None,
        data_inicio,
        data_fim,
        current_user_perfil,
        current_user_loja_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[AuditoriaEvento], int]:
        from app.schemas.utilizador import PerfilUtilizador as P
        itens = list(self._data)
        if current_user_perfil != P.ADMINISTRADOR:
            itens = [i for i in itens if i.loja_id == current_user_loja_id]
        elif loja_id is not None:
            itens = [i for i in itens if i.loja_id == loja_id]
        if evento is not None:
            itens = [i for i in itens if i.evento.value == evento]
        if utilizador_id is not None:
            itens = [i for i in itens if i.utilizador_id == utilizador_id]
        if data_inicio is not None:
            itens = [i for i in itens if i.timestamp.date() >= data_inicio]
        if data_fim is not None:
            itens = [i for i in itens if i.timestamp.date() <= data_fim]
        total = len(itens)
        start = (page - 1) * page_size
        return itens[start : start + page_size], total
