from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import check_connection

app = FastAPI(
    title="DLMCare API",
    description="Sistema de gestão para cadeia de oficinas de reparação de trotinetes elétricas.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


# ── Exception Handlers ───────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Converte os erros 422 do FastAPI para o formato padrão do contrato."""
    # Extrai a primeira mensagem de erro da lista gerada pelo Pydantic
    erro_msg = exc.errors()[0].get("msg", "Erro de validação nos dados enviados.")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": erro_msg, "code": "VALIDATION_ERROR"},
    )


# ── Health check ─────────────────────────────────────────────
@app.get("/health", tags=["sistema"])
def health():
    db_ok = check_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "env": settings.APP_ENV,
    }


# ── Routers ───────────────────────────────────────────────────────────────────
from app.routers import auth, clientes, trotinetes, pecas, stock, ordens_servico, faturas, dashboard, auditoria, utilizadores, lojas, notificacoes, transferencias, pedidos_peca, servicos, salarios

app.include_router(auth.router,            prefix="/api/v1")
app.include_router(clientes.router,        prefix="/api/v1")
app.include_router(trotinetes.router,      prefix="/api/v1")
app.include_router(pecas.router,           prefix="/api/v1")
app.include_router(stock.router,           prefix="/api/v1")
app.include_router(ordens_servico.router,  prefix="/api/v1")
app.include_router(faturas.router,         prefix="/api/v1")
app.include_router(dashboard.router,       prefix="/api/v1")
app.include_router(auditoria.router,       prefix="/api/v1")
app.include_router(utilizadores.router,    prefix="/api/v1")
app.include_router(lojas.router,           prefix="/api/v1")
app.include_router(notificacoes.router,    prefix="/api/v1")
app.include_router(transferencias.router,  prefix="/api/v1")
app.include_router(pedidos_peca.router,    prefix="/api/v1")
app.include_router(servicos.router,        prefix="/api/v1")
app.include_router(salarios.router,        prefix="/api/v1")
