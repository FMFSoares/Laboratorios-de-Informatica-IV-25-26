# backend/tests/conftest.py

import sys
import os
import pytest
from datetime import datetime
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
from app.schemas.ordem_servico import EstadoOrdemServico

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
    
    try:
        # --- SEED BÁSICO PARA OS TESTES ---
        loja1 = Loja(nome="Loja Origem", cidade="Braga", morada="Rua X", telefone="912345678", ativo=True)
        loja2 = Loja(nome="Loja Destino", cidade="Porto", morada="Rua Y", telefone="912345679", ativo=True)
        db.add_all([loja1, loja2])
        db.commit()
        db.refresh(loja1)
        db.refresh(loja2)
        
        # Peças e Stock
        peca1 = Peca(referencia="PNEU-001", nome="Pneu Michelin", categoria="PNEU", unidade="unidade", preco_custo=10.0, preco_venda=25.0)
        peca2 = Peca(referencia="TRAVAO-002", nome="Pastilhas de Travão", categoria="TRAVAO", unidade="par", preco_custo=5.0, preco_venda=15.0)
        db.add_all([peca1, peca2])
        db.commit()
        db.refresh(peca1)
        db.refresh(peca2)

        stock_peca1 = StockLoja(loja_id=loja1.id, peca_id=peca1.id, quantidade=10)
        stock_peca2 = StockLoja(loja_id=loja1.id, peca_id=peca2.id, quantidade=5)
        db.add_all([stock_peca1, stock_peca2])

        # Cliente e Trotinete
        # FIX: Adicionado 'data_registo' para satisfazer a constraint NOT NULL.
        cliente1 = Cliente(nome="Cliente Teste", nif="253333444", telemovel="911111111", email="cliente@teste.pt", consentimento_rgpd=True, data_registo=datetime.utcnow(), loja_id=loja1.id)
        db.add(cliente1)
        db.commit()
        db.refresh(cliente1)

        trotinete1 = Trotinete(
            cliente_id=cliente1.id,
            marca="Xiaomi",
            modelo="M365",
            numero_serie="SN-TEST-001",
            data_registo=datetime.now(),
        )
        db.add(trotinete1)
        db.commit()
        db.refresh(trotinete1)

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

        # Ordem de Serviço inicial (em estado 'ABERTA')
        os1 = OrdemServico(
            trotinete_id=trotinete1.id,
            cliente_id=cliente1.id,   # <-- adicionar isto
            loja_id=loja1.id,
            descricao_problema="Revisão geral",
            estado=EstadoOrdemServico.PENDENTE,
            prioridade="NORMAL",
            preco_servico=20.0,
            data_entrada=datetime.now(),
        )
        db.add(os1)
        db.commit()

        yield db  # Cede a sessão para o teste
    
    finally:
        # FIX: A limpeza é feita num bloco finally para garantir que é sempre executada,
        # mesmo que ocorra um erro durante o "seeding" dos dados.
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

@pytest.fixture(scope="function")
def admin_client(client):
    """Um TestClient autenticado como Administrador."""
    token = client.post("/api/v1/auth/login", json={"email": "admin@teste.pt", "password": "admin123"}).json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

@pytest.fixture(scope="function")
def gerente_client(client):
    """Um TestClient autenticado como Gerente de Loja."""
    token = client.post("/api/v1/auth/login", json={"email": "gerente@teste.pt", "password": "gerente123"}).json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

@pytest.fixture(scope="function")
def rec_client(client):
    """Um TestClient autenticado como Rececionista."""
    token = client.post("/api/v1/auth/login", json={"email": "rec@teste.pt", "password": "rec123"}).json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

@pytest.fixture(scope="function")
def mec_client(client):
    """Um TestClient autenticado como Mecânico."""
    token = client.post("/api/v1/auth/login", json={"email": "mecanico@teste.pt", "password": "mecanico123"}).json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client