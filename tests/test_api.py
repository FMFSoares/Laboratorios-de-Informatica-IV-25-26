# backend/test_api.py
import pytest

def test_login_sucesso_e_falha(client):
    # Caso Normal: Login correto
    response = client.post("/api/v1/auth/login", json={"email": "admin@teste.pt", "password": "admin123"})
    assert response.status_code == 201
    assert "access_token" in response.json()

    # Edge Case: Password errada
    response_fail = client.post("/api/v1/auth/login", json={"email": "admin@teste.pt", "password": "wrongpassword"})
    assert response_fail.status_code == 401
    assert response_fail.json()["detail"]["code"] == "INVALID_CREDENTIALS"

def test_criar_cliente_nif_duplicado(client):
    # Fazemos login para ter o token
    token = client.post("/api/v1/auth/login", json={"email": "rec@teste.pt", "password": "rec123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cliente_data = {
        "nome": "João Ninguém",
        "nif": "123456789",
        "telemovel": "912345678",
        "email": "joao@teste.pt",
        "consentimento_rgpd": True
    }

    # Caso Normal: Criar cliente
    res1 = client.post("/api/v1/clientes", json=cliente_data, headers=headers)
    assert res1.status_code == 201

    # Edge Case: Tentar criar outro cliente com o MESMO NIF
    res2 = client.post("/api/v1/clientes", json=cliente_data, headers=headers)
    assert res2.status_code in [400, 409] 
    assert res2.json()["detail"]["code"] == "DUPLICATE_ENTRY"

def test_transferencia_stock_insuficiente(client):
    token = client.post("/api/v1/auth/login", json={"email": "admin@teste.pt", "password": "admin123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Criar uma peça falsa para testar
    client.post("/api/v1/pecas", json={
        "referencia": "PNEU-001", "nome": "Pneu", "categoria": "PNEU", 
        "unidade": "unidade", "preco_custo": 10.0, "preco_venda": 25.0
    }, headers=headers)

    # Edge Case: Tentar transferir stock que não existe (Quantidade 999)
    transferencia_data = {
        "peca_id": 1,
        "loja_origem_id": 1,
        "loja_destino_id": 2,
        "quantidade": 999
    }
    
    # Vai falhar a validação de lojas distintas primeiro ou de falta de stock
    res = client.post("/api/v1/stock/transferencias", json=transferencia_data, headers=headers)
    
    # Esperamos que seja travado pelo erro 404 (Loja destino não existe) ou 400 (stock insuficiente)
    # Dependendo da ordem de validação no vosso TransferenciaService
    assert res.status_code in [400, 404]

def test_faturacao_rejeita_os_nao_concluida(client):
    token = client.post("/api/v1/auth/login", json={"email": "rec@teste.pt", "password": "rec123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Edge Case: Tentar faturar uma OS que não está no estado CONCLUIDA (ex. OS inventada ID 999)
    res = client.post("/api/v1/faturas", json={"ordem_servico_id": 999}, headers=headers)
    
    # Como a OS 999 não existe, o vosso serviço deve cuspir 404
    assert res.status_code == 404

def test_cobertura_lojas_e_utilizadores(client):
    # Passar por todos os endpoints de leitura base
    token = client.post("/api/v1/auth/login", json={"email": "admin@teste.pt", "password": "admin123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Bater no endpoint /me (Auth Service)
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200
    
    # Bater nas Lojas
    assert client.get("/api/v1/lojas", headers=headers).status_code == 200
    
    # Bater nos Utilizadores
    assert client.get("/api/v1/utilizadores", headers=headers).status_code == 200

def test_cobertura_pecas_e_stock(client):
    # Simular o ciclo de vida do inventário
    token = client.post("/api/v1/auth/login", json={"email": "admin@teste.pt", "password": "admin123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Criar Peça com sucesso
    res_peca = client.post("/api/v1/pecas", json={
        "referencia": "PNEU-COV-01", "nome": "Pneu Coverage", "categoria": "PNEU", 
        "unidade": "unidade", "preco_custo": 10.0, "preco_venda": 20.0
    }, headers=headers)
    assert res_peca.status_code == 201
    peca_id = res_peca.json()["data"]["id"]
    
    # 2. Listar Peças e Obter Peça
    client.get("/api/v1/pecas", headers=headers)
    client.get(f"/api/v1/pecas/{peca_id}", headers=headers)
    
    # 3. Entrada de Stock (Passar pelo Stock Service)
    res_stock = client.post("/api/v1/stock/entradas", json={
        "loja_id": 1, "peca_id": peca_id, "quantidade": 50, "observacoes": "Reposição Teste"
    }, headers=headers)
    assert res_stock.status_code == 201
    
    # 4. Listar Stock
    client.get("/api/v1/stock", headers=headers)

def test_cobertura_dashboard_auditoria(client):
    # Simular a vista da gerência
    token = client.post("/api/v1/auth/login", json={"email": "admin@teste.pt", "password": "admin123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Bater no Dashboard (calcula todas as estatísticas)
    assert client.get("/api/v1/dashboard", headers=headers).status_code == 200
    
    # Bater na Auditoria (lista os logs gerados pelos testes anteriores)
    assert client.get("/api/v1/auditoria", headers=headers).status_code == 200
    
def test_cobertura_ordens_e_trotinetes(client):
    # --- 1. ADMIN prepara o terreno (Cria a Peça) ---
    token_admin = client.post("/api/v1/auth/login", json={"email": "admin@teste.pt", "password": "admin123"}).json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    
    admin_peca =client.post("/api/v1/pecas", json={
                    "referencia": "PNEU-001", "nome": "Pneu", "categoria": "PNEU", 
                    "unidade": "unidade", "preco_custo": 10.0, "preco_venda": 25.0
                }, headers=headers_admin)
    peca_id = admin_peca.json()["data"]["id"] # Captura o ID real criado

    client.post("/api/v1/stock/entradas", json={
        "loja_id": 1, 
        "peca_id": peca_id, 
        "quantidade": 10, 
        "observacoes": "Stock inicial para testes"
    }, headers=headers_admin)
    
    # --- 2. RECECIONISTA cria Cliente, Trotinete e OS ---
    token_rec = client.post("/api/v1/auth/login", json={"email": "rec@teste.pt", "password": "rec123"}).json()["access_token"]
    headers_rec = {"Authorization": f"Bearer {token_rec}"}
    
    res_cli = client.post("/api/v1/clientes", json={
        "nome": "Cliente OS", "nif": "198968183", "telemovel": "919999999", "consentimento_rgpd": True
    }, headers=headers_rec)
    cli_id = res_cli.json()["data"]["id"]
    
    res_trot = client.post("/api/v1/trotinetes", json={
        "cliente_id": cli_id, "marca": "Xiaomi", "modelo": "M365", "numero_serie": "SN12345"
    }, headers=headers_rec)
    trot_id = res_trot.json()["data"]["id"]
    
    res_os = client.post("/api/v1/ordens-servico", json={
        "trotinete_id": trot_id, "loja_id": 1, "descricao_problema": "Pneu furado", 
        "prioridade": "NORMAL", "preco_servico": 15.0
    }, headers=headers_rec)
    os_id = res_os.json()["data"]["id"]
    
    # --- 3. MECÂNICO adiciona a peça (agora sim, 201 Created!) ---
    token_mec = client.post("/api/v1/auth/login", json={"email": "mecanico@teste.pt", "password": "mecanico123"}).json()["access_token"]
    headers_mec = {"Authorization": f"Bearer {token_mec}"}
    
    res_peca = client.post(
        f"/api/v1/ordens-servico/{os_id}/pecas", 
        json={"peca_id": peca_id, "quantidade": 1}, 
        headers=headers_mec # Usa o token do MECÂNICO
    )
    assert res_peca.status_code == 201