# ── Utilitários comuns ────────────────────────────────────────────────────────
from app.schemas.common import (
    DataResponse,
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
    validate_nif,
    validate_telemovel,
)

# ── Enums ─────────────────────────────────────────────────────────────────────
from app.schemas.utilizador import PerfilUtilizador
from app.schemas.peca import CategoriaPeca
from app.schemas.stock import TipoMovimentoStock
from app.schemas.ordem_servico import EstadoOrdemServico, PrioridadeOrdemServico
from app.schemas.fatura import EstadoFatura
from app.schemas.auditoria import TipoEventoAuditoria

# ── Autenticação ──────────────────────────────────────────────────────────────
from app.schemas.auth import (
    AuthUserInfo,
    CurrentUserResponse,
    LoginRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TokenResponse,
)

# ── Utilizadores ──────────────────────────────────────────────────────────────
from app.schemas.utilizador import (
    UtilizadorBase,
    UtilizadorResponse,
    UtilizadorResumo,
)

# ── Lojas ─────────────────────────────────────────────────────────────────────
from app.schemas.loja import LojaBase, LojaResponse, LojaResumo

# ── Clientes ──────────────────────────────────────────────────────────────────
from app.schemas.cliente import (
    ClienteCreate,
    ClienteDetalheResponse,
    ClienteHistoricoItem,
    ClienteResponse,
    ClienteResumo,
)

# ── Trotinetes ────────────────────────────────────────────────────────────────
from app.schemas.trotinete import (
    TrotineteCreate,
    TrotineteDetalheResponse,
    TrotineteResponse,
    TrotineteResumo,
)

# ── Peças ─────────────────────────────────────────────────────────────────────
from app.schemas.peca import (
    PecaCreate,
    PecaDetalheResponse,
    PecaResponse,
    PecaResumo,
)

# ── Stock ─────────────────────────────────────────────────────────────────────
from app.schemas.stock import (
    StockEntradaRequest,
    StockEntradaResponse,
    StockItemResponse,
    StockTransferenciaRequest,
    StockTransferenciaResponse,
)

# ── Ordens de Serviço ─────────────────────────────────────────────────────────
from app.schemas.ordem_servico import (
    OrdemServicoCreate,
    OrdemServicoDetalheResponse,
    OrdemServicoEstadoUpdate,
    OrdemServicoEstadoUpdateResponse,
    OrdemServicoResponse,
    OrdemServicoResumo,
    PecaAplicadaRequest,
    PecaAplicadaResponse,
    PecaAplicadaResumo,
    TempoParagemResponse,
    TempoInicioResponse,
)

# ── Faturas ───────────────────────────────────────────────────────────────────
from app.schemas.fatura import (
    FaturaClienteInfo,
    FaturaCreateRequest,
    FaturaLojaInfo,
    FaturaPecaAplicada,
    FaturaResponse,
    FaturaResumo,
    FaturaServicoInfo,
    FaturaTrotineteInfo,
)

# ── Dashboard ─────────────────────────────────────────────────────────────────
from app.schemas.dashboard import (
    DashboardPeriodo,
    DashboardResponse,
    EficienciaMecanico,
    FaturacaoPorLoja,
    OrdensConcluidasPorLoja,
    PecaAbaixoStockMinimo,
)

# ── Auditoria ─────────────────────────────────────────────────────────────────
from app.schemas.auditoria import AuditoriaDetalhe, AuditoriaItemResponse

__all__ = [
    # common
    "DataResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationParams",
    "validate_nif",
    "validate_telemovel",
    # enums
    "PerfilUtilizador",
    "CategoriaPeca",
    "TipoMovimentoStock",
    "EstadoOrdemServico",
    "PrioridadeOrdemServico",
    "EstadoFatura",
    "TipoEventoAuditoria",
    # auth
    "AuthUserInfo",
    "CurrentUserResponse",
    "LoginRequest",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "TokenResponse",
    # utilizadores
    "UtilizadorBase",
    "UtilizadorResponse",
    "UtilizadorResumo",
    # lojas
    "LojaBase",
    "LojaResponse",
    "LojaResumo",
    # clientes
    "ClienteCreate",
    "ClienteDetalheResponse",
    "ClienteHistoricoItem",
    "ClienteResponse",
    "ClienteResumo",
    # trotinetes
    "TrotineteCreate",
    "TrotineteDetalheResponse",
    "TrotineteResponse",
    "TrotineteResumo",
    # peças
    "PecaCreate",
    "PecaDetalheResponse",
    "PecaResponse",
    "PecaResumo",
    # stock
    "StockEntradaRequest",
    "StockEntradaResponse",
    "StockItemResponse",
    "StockTransferenciaRequest",
    "StockTransferenciaResponse",
    # ordens de serviço
    "OrdemServicoCreate",
    "OrdemServicoDetalheResponse",
    "OrdemServicoEstadoUpdate",
    "OrdemServicoEstadoUpdateResponse",
    "OrdemServicoResponse",
    "OrdemServicoResumo",
    "PecaAplicadaRequest",
    "PecaAplicadaResponse",
    "PecaAplicadaResumo",
    "TempoInicioResponse",
    "TempoParagemResponse",
    # faturas
    "FaturaClienteInfo",
    "FaturaCreateRequest",
    "FaturaLojaInfo",
    "FaturaPecaAplicada",
    "FaturaResponse",
    "FaturaResumo",
    "FaturaServicoInfo",
    "FaturaTrotineteInfo",
    # dashboard
    "DashboardPeriodo",
    "DashboardResponse",
    "EficienciaMecanico",
    "FaturacaoPorLoja",
    "OrdensConcluidasPorLoja",
    "PecaAbaixoStockMinimo",
    # auditoria
    "AuditoriaDetalhe",
    "AuditoriaItemResponse",
]
