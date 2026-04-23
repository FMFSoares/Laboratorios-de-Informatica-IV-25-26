from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # verifica a ligação antes de usar
    pool_recycle=3600,        # recicla ligações ao fim de 1 hora
    echo=settings.APP_DEBUG,  # mostra SQL no terminal em dev
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy."""
    pass


def get_db():
    """Dependency FastAPI — injeta sessão de BD e garante fecho."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_connection() -> bool:
    """Verifica se a ligação à BD está operacional."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
