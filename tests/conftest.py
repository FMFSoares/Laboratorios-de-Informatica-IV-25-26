# backend/tests/conftest.py

import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

# 1. Mock das Variáveis
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "super-segredo-de-testes-li4-2026"
os.environ["APP_ENV"] = "test"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool  # <--- A MAGIA ESTÁ AQUI

from app.main import app
from app.database import Base, get_db
from app.core.security import hash_password

# 2. Importar TODOS os modelos para o SQLAlchemy saber que eles existem e criar as tabelas!
from app.models.loja import Loja
from app.models.utilizador import Utilizador
from app.models.cliente import Cliente
from app.models.trotinete import Trotinete
from app.models.ordem_servico import OrdemServico, OSPeca, RegistoTempo
from app.models.peca import Peca
from app.models.stock import StockLoja
from app.models.fatura import Fatura
from app.models.auditoria import Auditoria
from app.models.transferencia import PedidoTransferencia, PedidoPeca
from app.models.notificacao import Notificacao
from app.schemas.utilizador import PerfilUtilizador

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# 3. poolclass=StaticPool garante que a BD não sofre de "amnésia" entre threads!
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool 
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Cria todas as tabelas!
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # --- SEED BÁSICO PARA OS TESTES ---
    loja1 = Loja(nome="Loja Origem", cidade="Braga", morada="Rua X", telefone="912345678", ativo=True)
    loja2 = Loja(nome="Loja Destino", cidade="Porto", morada="Rua Y", telefone="912345679", ativo=True)
    db.add_all([loja1, loja2])
    db.commit()
    db.refresh(loja1)
    
    admin = Utilizador(
        nome="Admin", email="admin@teste.pt", password_hash=hash_password("admin123"), 
        perfil=PerfilUtilizador.ADMINISTRADOR, ativo=True
    )
    gerente = Utilizador(
        nome="Gerente", email="gerente@teste.pt", password_hash=hash_password("gerente123"), 
        perfil=PerfilUtilizador.GERENTE_LOJA, loja_id=loja1.id, ativo=True
    )
    rececionista = Utilizador(
        nome="Rececionista", email="rec@teste.pt", password_hash=hash_password("rec123"), 
        perfil=PerfilUtilizador.RECECIONISTA, loja_id=loja1.id, ativo=True
    )
    mecanico = Utilizador(
        nome="Mecanico", email="mecanico@teste.pt", password_hash=hash_password("mecanico123"), 
        perfil=PerfilUtilizador.MECANICO, loja_id=loja1.id, ativo=True
    )
    db.add_all([admin, gerente, rececionista, mecanico])
    db.commit()

    yield db  # Cede a sessão para o teste
    
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()