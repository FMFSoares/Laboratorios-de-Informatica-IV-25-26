from fastapi import FastAPI
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
    allow_methods=["*"],
    allow_headers=["*"],
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
from app.routers import auth, clientes, trotinetes, pecas, stock, ordens_servico

app.include_router(auth.router,           prefix="/api/v1")
app.include_router(clientes.router,       prefix="/api/v1")
app.include_router(trotinetes.router,     prefix="/api/v1")
app.include_router(pecas.router,          prefix="/api/v1")
app.include_router(stock.router,          prefix="/api/v1")
app.include_router(ordens_servico.router, prefix="/api/v1")
# app.include_router(ordens_servico.router, prefix="/api/v1")
# app.include_router(stock.router,          prefix="/api/v1")
# app.include_router(faturas.router,        prefix="/api/v1")
# app.include_router(dashboard.router,      prefix="/api/v1")
# app.include_router(auditoria.router,      prefix="/api/v1")
