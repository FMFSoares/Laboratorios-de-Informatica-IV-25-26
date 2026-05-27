# backend/test_api.py
import pytest
import uuid

def test_login_sucesso_e_falha(client):
    # Caso Normal: Login correto
    response = client.post("/api/v1/auth/login", json={"email": "admin@teste.pt", "password": "admin123"})
    assert response.status_code == 201
    assert "access_token" in response.json()

    # Edge Case: Password errada
    response_fail = client.post("/api/v1/auth/login", json={"email": "admin@teste.pt", "password": "wrongpassword"})
    assert response_fail.status_code == 401
    assert response_fail.json()["detail"]["code"] == "INVALID_CREDENTIALS"

def test_criar_cliente_nif_duplicado(rec_client):
    cliente_data = {
        "nome": "João Ninguém",
        "nif": "123456789",
        "telemovel": "912345678",
        "email": "joao@teste.pt",
        "consentimento_rgpd": True,
    }

    # Caso Normal: Criar cliente
    res1 = rec_client.post("/api/v1/clientes", json=cliente_data)
    assert res1.status_code == 201

    # Edge Case: Tentar criar outro cliente com o MESMO NIF
    res2 = rec_client.post("/api/v1/clientes", json=cliente_data)
    assert res2.status_code in [400, 409]
    assert res2.json()["detail"]["code"] == "DUPLICATE_ENTRY"

def test_transferencia_stock_insuficiente(admin_client):
    # A peça 1 e a loja 1 são criadas no conftest. A peça 1 tem 10 de stock na loja 1.
    # Tentamos transferir 11 unidades, o que deve falhar.
    transferencia_data = {
        "peca_id": 1,  # Peca "PNEU-001"
        "loja_origem_id": 1,  # Loja "Braga"
        "loja_destino_id": 2,  # Loja "Porto"
        "quantidade": 11,  # Mais do que o stock de 10
    }

    res = admin_client.post("/api/v1/stock/transferencias", json=transferencia_data)

    # A validação de stock deve ser prioritária e falhar.
    assert res.status_code == 400
    assert "insuficiente" in res.json()["detail"].lower()

def test_faturacao_rejeita_os_nao_concluida(rec_client):
    # Edge Case: Tentar faturar uma OS que não está no estado CONCLUIDA (ex. OS inventada ID 999)
    res = rec_client.post("/api/v1/faturas", json={"ordem_servico_id": 999})

    # Como a OS 999 não existe, o vosso serviço deve cuspir 404
    assert res.status_code == 404

    # Caso 2: Tentar faturar a OS 1, que foi criada no conftest em estado 'ABERTA'
    res_nao_concluida = rec_client.post("/api/v1/faturas", json={"ordem_servico_id": 1})
    assert res_nao_concluida.status_code == 400  # Ou 409, dependendo da implementação
    assert res_nao_concluida.json()["detail"]["code"] == "ORDER_NOT_CONCLUDED"

def test_cobertura_lojas_e_utilizadores(admin_client):
    # Passar por todos os endpoints de leitura base
    # Bater no endpoint /me (Auth Service)
    assert admin_client.get("/api/v1/auth/me").status_code == 200

    # Bater nas Lojas
    assert admin_client.get("/api/v1/lojas").status_code == 200

    # Bater nos Utilizadores
    assert admin_client.get("/api/v1/utilizadores").status_code == 200

def test_cobertura_pecas_e_stock(admin_client):
    # Simular o ciclo de vida do inventário
    # 1. Criar Peça com sucesso
    res_peca = admin_client.post(
        "/api/v1/pecas",
        json={
            "referencia": "PNEU-COV-01",
            "nome": "Pneu Coverage",
            "categoria": "PNEU",
            "unidade": "unidade",
            "preco_custo": 10.0,
            "preco_venda": 20.0,
        },
    )
    assert res_peca.status_code == 201
    peca_id = res_peca.json()["data"]["id"]

    # 2. Listar Peças e Obter Peça
    admin_client.get("/api/v1/pecas")
    admin_client.get(f"/api/v1/pecas/{peca_id}")

    # 3. Entrada de Stock (Passar pelo Stock Service)
    res_stock = admin_client.post(
        "/api/v1/stock/entradas",
        json={
            "loja_id": 1,
            "peca_id": peca_id,
            "quantidade": 50,
            "observacoes": "Reposição Teste",
        },
    )
    assert res_stock.status_code == 201

    # 4. Listar Stock
    admin_client.get("/api/v1/stock")

def test_cobertura_dashboard_auditoria(admin_client):
    # Simular a vista da gerência
    # Bater no Dashboard (calcula todas as estatísticas)
    assert admin_client.get("/api/v1/dashboard").status_code == 200

    # Bater na Auditoria (lista os logs gerados pelos testes anteriores)
    assert admin_client.get("/api/v1/auditoria").status_code == 200

def test_rececionista_cria_os_para_cliente_existente(rec_client):
    """ Testa se um rececionista pode criar uma OS para um cliente e trotinete já existentes (criados no conftest). """
    res_os = rec_client.post(
        "/api/v1/ordens-servico",
        json={
            "trotinete_id": 1,  # Usa a trotinete criada no conftest
            "loja_id": 1,
            "descricao_problema": "Pneu furado",
            "prioridade": "NORMAL",
            "preco_servico": 15.0,
        },
    )
    assert res_os.status_code == 201
    assert res_os.json()["data"]["descricao_problema"] == "Pneu furado"

def test_mecanico_adiciona_peca_a_os(mec_client):
    """ Testa se um mecânico pode adicionar uma peça com stock a uma OS existente. """
    res_peca = mec_client.post(
        "/api/v1/ordens-servico/1/pecas",  # Usa a OS 1 do conftest
        json={"peca_id": 1, "quantidade": 1},  # Usa a Peça 1 do conftest (tem stock)
    )
    if res_peca.status_code != 201:
        print(f"DEBUG ERRO POST: {res_peca.json()}")
    assert res_peca.status_code == 201
    assert res_peca.json()["data"]["quantidade"] == 1

def test_mecanico_falha_adicionar_peca_sem_stock_suficiente(mec_client):
    """ Testa a falha ao tentar adicionar mais peças do que as existentes em stock. """
    # A peça 1 (Pneu) tem 10 unidades em stock no conftest. Tentar adicionar 11.
    res_peca = mec_client.post(
        "/api/v1/ordens-servico/1/pecas", json={"peca_id": 1, "quantidade": 11}
    )
    assert res_peca.status_code == 400
    assert "insuficiente" in res_peca.json()["detail"].lower()


# --- Testes de Permissões (RBAC) ---


@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("admin_client", 201),
        ("gerente_client", 201),
        ("rec_client", 403),
        ("mec_client", 403),
    ],
)
def test_criar_peca_permissoes(user_fixture, expected_status, request):
    """Testa a matriz de permissões para a criação de peças."""
    client = request.getfixturevalue(user_fixture)

    # Usar uma referência única para cada execução para evitar conflitos de BD
    peca_ref = f"REF-{uuid.uuid4()}"

    peca_data = {
        "referencia": peca_ref,
        "nome": "Peça de Teste de Permissão",
        "categoria": "PNEU",
        "unidade": "unidade",
        "preco_custo": 5.0,
        "preco_venda": 10.0,
    }

    response = client.post("/api/v1/pecas", json=peca_data)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("admin_client", 201),
        ("gerente_client", 201),  # Gerentes podem precisar de adicionar peças
        ("mec_client", 201),
        ("rec_client", 403),
    ],
)
def test_adicionar_peca_os_permissoes(user_fixture, expected_status, request):
    """Testa a matriz de permissões para adicionar peças a uma Ordem de Serviço."""
    client = request.getfixturevalue(user_fixture)

    # Usa a OS 1 e a Peça 2 (Travão) do conftest. A Peça 2 tem 5 de stock.
    os_peca_data = {"peca_id": 2, "quantidade": 1}

    response = client.post("/api/v1/ordens-servico/1/pecas", json=os_peca_data)
    assert response.status_code == expected_status

def test_transferencia_peca_inexistente(admin_client):
    """Tenta transferir uma peça que não existe no catálogo."""
    res = admin_client.post("/api/v1/stock/transferencias", json={
        "peca_id": 9999, "loja_origem_id": 1, "loja_destino_id": 2, "quantidade": 1
    })
    assert res.status_code == 404

def test_transferencia_loja_inexistente(admin_client):
    """Tenta transferir entre lojas inexistentes."""
    res = admin_client.post("/api/v1/stock/transferencias", json={
        "peca_id": 1, "loja_origem_id": 99, "loja_destino_id": 88, "quantidade": 1
    })
    assert res.status_code in [404, 400]

def test_adicionar_peca_os_inexistente(mec_client):
    """Testa a falha ao tentar adicionar peças numa OS que não existe."""
    res = mec_client.post("/api/v1/ordens-servico/99999/pecas", json={"peca_id": 1, "quantidade": 1})
    assert res.status_code == 404

def test_atualizar_estado_os_invalido(admin_client):
    """Testa a tentativa de mudar a OS para um estado inválido (se existir essa lógica)."""
    res = admin_client.patch("/api/v1/ordens-servico/1/estado", json={"novo_estado": "ESTADO_INEXISTENTE"})
    assert res.status_code == 422 # Erro de validação do Enum

# 1. Teste de Auditoria Completo (Cobre AuditoriaRepository)
def test_cobertura_fluxo_auditoria(admin_client):
    """Garante que ações de escrita geram entradas na auditoria."""
    # Ação de escrita
    admin_client.post("/api/v1/pecas", json={
        "referencia": "AUDIT-001", "nome": "Peça Audit", "categoria": "PNEU",
        "unidade": "unidade", "preco_custo": 1.0, "preco_venda": 2.0
    })
    
    # Verifica se o log foi registado
    res_auditoria = admin_client.get("/api/v1/auditoria")
    assert res_auditoria.status_code == 200
    logs = res_auditoria.json()["data"]
    assert len(logs) > 0
    # Verifica se a última ação foi a criação da peça
    assert "PECA_CRIADA" in logs[0]["evento"]

# 2. Teste de Estado Inválido (Cobre OrdemServicoService - ramos de erro)
def test_ordem_servico_transicao_estado_invalida(admin_client):
    """Tenta atualizar estado para algo que não existe."""
    # Usando o endpoint de atualização de estado
    res = admin_client.patch(
        "/api/v1/ordens-servico/1/estado", 
        json={"estado": "ESTADO_INEXISTENTE"} # Isto vai falhar na validação do Pydantic
    )
    assert res.status_code == 422 

# 3. Teste de Paginação e Filtros (Cobre Repositories de Cliente e Peca)
@pytest.mark.parametrize("page, page_size", [(1, 5), (2, 2)])
def test_listagem_paginacao_e_filtros(admin_client, page, page_size):
    """Testa os parâmetros de paginação nos repositórios."""
    # Lista clientes com paginação
    res = admin_client.get(f"/api/v1/clientes?page={page}&page_size={page_size}")
    assert res.status_code == 200
    data = res.json()
    assert "data" in data
    assert len(data["data"]) <= page_size

# 4. Teste de Erro de Stock no Service (Cobre StockService.consumir_stock)
def test_stock_consumo_excessivo_service(mec_client):
    """Força erro de stock insuficiente via service."""
    # Peca 1 tem 10 de stock no conftest. Pedir 999.
    res = mec_client.post("/api/v1/ordens-servico/1/pecas", json={"peca_id": 1, "quantidade": 999})
    assert res.status_code == 400