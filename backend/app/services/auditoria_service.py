from __future__ import annotations

# [pendente de integração com BD]
# Registos de auditoria estáticos para a Etapa 3.
# Na integração real, cada service escreve na tabela `auditoria` em vez de
# acrescentar a esta lista.

from datetime import datetime, timezone

from app.schemas.auditoria import TipoEventoAuditoria as E, AuditoriaItemResponse
from app.schemas.auth import CurrentUserResponse
from app.schemas.common import PaginatedResponse
from app.schemas.utilizador import PerfilUtilizador as P

# ── Mock data ─────────────────────────────────────────────────────────────────

_MOCK_AUDITORIA: list[dict] = [
    {
        "id": 1,
        "evento": E.LOGIN_SUCESSO,
        "descricao": "Login efetuado com sucesso.",
        "utilizador_id": 3,
        "utilizador_nome": "Ana Rececionista",
        "loja_id": 1,
        "ip_origem": "192.168.1.10",
        "timestamp": datetime(2026, 4, 28, 9, 0, tzinfo=timezone.utc),
        "detalhe": {"email": "ana.lisboa@dlmcare.pt"},
    },
    {
        "id": 2,
        "evento": E.OS_ESTADO_ALTERADO,
        "descricao": "OS #1 alterada de PENDENTE para EM_DIAGNOSTICO.",
        "utilizador_id": 4,
        "utilizador_nome": "João Mecânico",
        "loja_id": 1,
        "ip_origem": "192.168.1.11",
        "timestamp": datetime(2026, 4, 28, 10, 0, tzinfo=timezone.utc),
        "detalhe": {"ordem_servico_id": 1, "estado_anterior": "PENDENTE", "estado_novo": "EM_DIAGNOSTICO"},
    },
    {
        "id": 3,
        "evento": E.STOCK_ENTRADA,
        "descricao": "Entrada de stock: 10 unidades de PEC-BAT-001 na loja 1.",
        "utilizador_id": 1,
        "utilizador_nome": "Admin DLMCare",
        "loja_id": 1,
        "ip_origem": "192.168.1.1",
        "timestamp": datetime(2026, 4, 28, 11, 0, tzinfo=timezone.utc),
        "detalhe": {"peca_id": 1, "loja_id": 1, "quantidade": 10},
    },
    {
        "id": 4,
        "evento": E.STOCK_TRANSFERENCIA,
        "descricao": "Transferência de 2 unidades de PEC-BAT-001 da loja 1 para loja 2.",
        "utilizador_id": 1,
        "utilizador_nome": "Admin DLMCare",
        "loja_id": 1,
        "ip_origem": "192.168.1.1",
        "timestamp": datetime(2026, 4, 28, 12, 0, tzinfo=timezone.utc),
        "detalhe": {"peca_id": 1, "loja_origem_id": 1, "loja_destino_id": 2, "quantidade": 2},
    },
    {
        "id": 5,
        "evento": E.FATURA_EMITIDA,
        "descricao": "Fatura FAT-2026-0001 emitida para OS #2.",
        "utilizador_id": 3,
        "utilizador_nome": "Ana Rececionista",
        "loja_id": 1,
        "ip_origem": "192.168.1.10",
        "timestamp": datetime(2026, 4, 28, 17, 0, tzinfo=timezone.utc),
        "detalhe": {"fatura_id": 1, "ordem_servico_id": 2, "valor_final": 33.90},
    },
    {
        "id": 6,
        "evento": E.ACESSO_NEGADO,
        "descricao": "Acesso negado: perfil MECANICO tentou aceder a POST /clientes.",
        "utilizador_id": 4,
        "utilizador_nome": "João Mecânico",
        "loja_id": 1,
        "ip_origem": "192.168.1.11",
        "timestamp": datetime(2026, 4, 28, 14, 30, tzinfo=timezone.utc),
        "detalhe": {"endpoint": "POST /api/v1/clientes", "perfil": "MECANICO"},
    },
    {
        "id": 7,
        "evento": E.LOGIN_FALHA,
        "descricao": "Tentativa de login falhada para o email desconhecido@dlmcare.pt.",
        "utilizador_id": None,
        "utilizador_nome": None,
        "loja_id": None,
        "ip_origem": "10.0.0.99",
        "timestamp": datetime(2026, 4, 28, 8, 55, tzinfo=timezone.utc),
        "detalhe": {"email": "desconhecido@dlmcare.pt"},
    },
]


# ── Casos de uso ──────────────────────────────────────────────────────────────


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
    itens = list(_MOCK_AUDITORIA)

    # Filtro de loja: ADMIN pode ver tudo ou filtrar; GERENTE vê só a sua loja
    if current_user.perfil != P.ADMINISTRADOR:
        itens = [i for i in itens if i["loja_id"] == current_user.loja_id]
    elif loja_id is not None:
        itens = [i for i in itens if i["loja_id"] == loja_id]

    if evento is not None:
        itens = [i for i in itens if i["evento"].value == evento]
    if utilizador_id is not None:
        itens = [i for i in itens if i["utilizador_id"] == utilizador_id]
    if data_inicio is not None:
        itens = [i for i in itens if i["timestamp"].date() >= data_inicio]
    if data_fim is not None:
        itens = [i for i in itens if i["timestamp"].date() <= data_fim]

    total = len(itens)
    pages = max(1, -(-total // page_size))
    start = (page - 1) * page_size

    return PaginatedResponse[AuditoriaItemResponse](
        data=[AuditoriaItemResponse(**i) for i in itens[start : start + page_size]],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
