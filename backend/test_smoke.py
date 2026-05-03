"""
Smoke tests para verificar os endpoints implementados até ao passo 10.
Corre sem base de dados — usa os mocks em memória.
"""

import os
os.environ["DATABASE_URL"] = "mysql+pymysql://test:test@localhost/test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-dlmcare-2026"
os.environ["APP_ENV"] = "test"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=True)

PASS = "✅"
FAIL = "❌"
results = []

def check(label: str, condition: bool, info: str = ""):
    status = PASS if condition else FAIL
    msg = f"  {status} {label}"
    if info:
        msg += f"  →  {info}"
    print(msg)
    results.append(condition)


# ─────────────────────────────────────────────────────────────────
print("\n── Health ──────────────────────────────────────────────")

r = client.get("/health")
check("GET /health → 200", r.status_code == 200)
check("health.status presente", "status" in r.json())


# ─────────────────────────────────────────────────────────────────
print("\n── Auth ────────────────────────────────────────────────")

# Login com credenciais erradas
r = client.post("/api/v1/auth/login", json={"email": "x@x.com", "password": "wrong"})
check("Login credenciais inválidas → 401", r.status_code == 401)
check("code = INVALID_CREDENTIALS", r.json()["detail"]["code"] == "INVALID_CREDENTIALS")

# Login válido — RECECIONISTA
r = client.post("/api/v1/auth/login", json={"email": "ana.lisboa@dlmcare.pt", "password": "password123"})
check("Login válido (RECECIONISTA) → 201", r.status_code == 201)
data = r.json()
check("access_token presente", "access_token" in data)
check("perfil = RECECIONISTA", data["user"]["perfil"] == "RECECIONISTA")
TOKEN_REC = data["access_token"]
REFRESH_TOKEN = data["refresh_token"]

# Login válido — ADMIN
r = client.post("/api/v1/auth/login", json={"email": "admin@dlmcare.pt", "password": "admin123"})
check("Login válido (ADMIN) → 201", r.status_code == 201)
TOKEN_ADMIN = r.json()["access_token"]

# Login válido — MECANICO
r = client.post("/api/v1/auth/login", json={"email": "joao.mecanico@dlmcare.pt", "password": "mecanico123"})
check("Login válido (MECANICO) → 201", r.status_code == 201)
TOKEN_MEC = r.json()["access_token"]

# GET /me
r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {TOKEN_REC}"})
check("GET /auth/me → 200", r.status_code == 200)
check("email correto no /me", r.json()["email"] == "ana.lisboa@dlmcare.pt")

# GET /me sem token
r = client.get("/api/v1/auth/me")
check("GET /auth/me sem token → 403", r.status_code == 403)

# Refresh
r = client.post("/api/v1/auth/refresh", json={"refresh_token": REFRESH_TOKEN})
check("POST /auth/refresh → 200", r.status_code == 200)
check("novo access_token presente", "access_token" in r.json())

# Refresh com token inválido
r = client.post("/api/v1/auth/refresh", json={"refresh_token": "token.invalido.mesmo"})
check("Refresh token inválido → 401", r.status_code == 401)


# ─────────────────────────────────────────────────────────────────
print("\n── Clientes ────────────────────────────────────────────")

HDR_REC   = {"Authorization": f"Bearer {TOKEN_REC}"}
HDR_ADMIN = {"Authorization": f"Bearer {TOKEN_ADMIN}"}
HDR_MEC   = {"Authorization": f"Bearer {TOKEN_MEC}"}

r = client.get("/api/v1/clientes", headers=HDR_REC)
check("GET /clientes → 200", r.status_code == 200)
check("devolve lista paginada", "data" in r.json() and "total" in r.json())
check("2 clientes mock presentes", r.json()["total"] >= 2)

# Filtro por NIF
r = client.get("/api/v1/clientes?query=123456789", headers=HDR_REC)
check("GET /clientes?query=NIF → 200", r.status_code == 200)
check("encontra 1 cliente por NIF", r.json()["total"] == 1)

# GET por ID
r = client.get("/api/v1/clientes/1", headers=HDR_REC)
check("GET /clientes/1 → 200", r.status_code == 200)
check("trotinetes populadas no detalhe", "trotinetes" in r.json()["data"])

# GET ID inexistente
r = client.get("/api/v1/clientes/999", headers=HDR_REC)
check("GET /clientes/999 → 404", r.status_code == 404)

# POST criar cliente
novo_cliente = {
    "nome": "Pedro Teste",
    "nif": "111222333",
    "telemovel": "931234567",
    "email": "pedro@teste.com",
    "morada": "Rua Teste 1",
    "consentimento_rgpd": True,
}
r = client.post("/api/v1/clientes", json=novo_cliente, headers=HDR_REC)
check("POST /clientes → 201", r.status_code == 201)
check("message presente", "message" in r.json())
ID_NOVO_CLIENTE = r.json()["data"]["id"]

# NIF duplicado
r = client.post("/api/v1/clientes", json=novo_cliente, headers=HDR_REC)
check("POST /clientes NIF duplicado → 409", r.status_code == 409)

# MECANICO não pode criar clientes
r = client.post("/api/v1/clientes", json={**novo_cliente, "nif": "999888777"}, headers=HDR_MEC)
check("MECANICO POST /clientes → 403", r.status_code == 403)

# RGPD obrigatório
r = client.post("/api/v1/clientes", json={**novo_cliente, "nif": "555444333", "consentimento_rgpd": False}, headers=HDR_REC)
check("POST /clientes sem RGPD → 422", r.status_code == 422)

# Histórico
r = client.get("/api/v1/clientes/1/historico", headers=HDR_REC)
check("GET /clientes/1/historico → 200", r.status_code == 200)


# ─────────────────────────────────────────────────────────────────
print("\n── Trotinetes ──────────────────────────────────────────")

r = client.get("/api/v1/trotinetes", headers=HDR_REC)
check("GET /trotinetes → 200", r.status_code == 200)
check("2 trotinetes mock presentes", r.json()["total"] >= 2)

r = client.get("/api/v1/trotinetes?cliente_id=1", headers=HDR_REC)
check("GET /trotinetes?cliente_id=1 → 200", r.status_code == 200)
check("filtra por cliente", r.json()["total"] >= 1)

r = client.get("/api/v1/trotinetes/1", headers=HDR_MEC)
check("GET /trotinetes/1 (MECANICO) → 200", r.status_code == 200)
check("campo cliente presente", "cliente" in r.json()["data"])

nova_trotinete = {
    "cliente_id": 1,
    "marca": "Segway",
    "modelo": "Ninebot F25",
    "numero_serie": "SG2026TEST999",
    "ano_compra": 2025,
    "cor": "Branco",
}
r = client.post("/api/v1/trotinetes", json=nova_trotinete, headers=HDR_REC)
check("POST /trotinetes → 201", r.status_code == 201)

r = client.post("/api/v1/trotinetes", json=nova_trotinete, headers=HDR_REC)
check("POST /trotinetes número série duplicado → 409", r.status_code == 409)

# MECANICO não pode criar trotinetes
r = client.post("/api/v1/trotinetes", json={**nova_trotinete, "numero_serie": "SG2026TEST000"}, headers=HDR_MEC)
check("MECANICO POST /trotinetes → 403", r.status_code == 403)


# ─────────────────────────────────────────────────────────────────
print("\n── Peças ───────────────────────────────────────────────")

r = client.get("/api/v1/pecas", headers=HDR_MEC)
check("GET /pecas (MECANICO) → 200", r.status_code == 200)
check("4 peças mock presentes", r.json()["total"] >= 4)

r = client.get("/api/v1/pecas?categoria=BATERIA", headers=HDR_REC)
check("GET /pecas?categoria=BATERIA → 200", r.status_code == 200)
check("filtra por categoria", all(p["categoria"] == "BATERIA" for p in r.json()["data"]))

r = client.get("/api/v1/pecas?query=pneu", headers=HDR_REC)
check("GET /pecas?query=pneu → 200 e encontra resultado", r.status_code == 200 and r.json()["total"] >= 1)

r = client.get("/api/v1/pecas/1", headers=HDR_REC)
check("GET /pecas/1 → 200", r.status_code == 200)
check("preco_custo NÃO exposto", "preco_custo" not in r.json()["data"])
check("preco_venda presente", "preco_venda" in r.json()["data"])

r = client.get("/api/v1/pecas/999", headers=HDR_REC)
check("GET /pecas/999 → 404", r.status_code == 404)

nova_peca = {
    "referencia": "PEC-TEST-001",
    "nome": "Peça de Teste",
    "categoria": "OUTRO",
    "unidade": "unidade",
    "preco_custo": 5.00,
    "preco_venda": 12.00,
}
r = client.post("/api/v1/pecas", json=nova_peca, headers=HDR_ADMIN)
check("POST /pecas (ADMIN) → 201", r.status_code == 201)
check("preco_custo NÃO na resposta do POST", "preco_custo" not in r.json()["data"])

# RECECIONISTA não pode criar peças
r = client.post("/api/v1/pecas", json={**nova_peca, "referencia": "PEC-TEST-002"}, headers=HDR_REC)
check("RECECIONISTA POST /pecas → 403", r.status_code == 403)


# ─────────────────────────────────────────────────────────────────
print("\n── Stock ───────────────────────────────────────────────")

r = client.get("/api/v1/stock", headers=HDR_REC)
check("GET /stock (RECECIONISTA) → 200", r.status_code == 200)
check("campo alerta presente", all("alerta" in s for s in r.json()["data"]))

r = client.get("/api/v1/stock?alerta=true", headers=HDR_REC)
check("GET /stock?alerta=true → 200", r.status_code == 200)
check("só devolve alertas", all(s["alerta"] for s in r.json()["data"]))

# Entrada de stock
r = client.post("/api/v1/stock/entradas",
    json={"loja_id": 1, "peca_id": 1, "quantidade": 10, "observacoes": "Reposição"},
    headers=HDR_ADMIN)
check("POST /stock/entradas (ADMIN) → 201", r.status_code == 201)
check("quantidade_anterior e quantidade_atual presentes", "quantidade_anterior" in r.json()["data"])

# RECECIONISTA não pode fazer entradas
r = client.post("/api/v1/stock/entradas",
    json={"loja_id": 1, "peca_id": 1, "quantidade": 5},
    headers=HDR_REC)
check("RECECIONISTA POST /stock/entradas → 403", r.status_code == 403)

# Transferência
r = client.post("/api/v1/stock/transferencias",
    json={"peca_id": 1, "loja_origem_id": 1, "loja_destino_id": 2, "quantidade": 2},
    headers=HDR_ADMIN)
check("POST /stock/transferencias (ADMIN) → 201", r.status_code == 201)

# Loja origem = destino → 422
r = client.post("/api/v1/stock/transferencias",
    json={"peca_id": 1, "loja_origem_id": 1, "loja_destino_id": 1, "quantidade": 1},
    headers=HDR_ADMIN)
check("transferencia loja_origem = loja_destino → 422", r.status_code == 422)

# Stock insuficiente
r = client.post("/api/v1/stock/transferencias",
    json={"peca_id": 3, "loja_origem_id": 2, "loja_destino_id": 1, "quantidade": 999},
    headers=HDR_ADMIN)
check("transferencia stock insuficiente → 400", r.status_code == 400)


# ─────────────────────────────────────────────────────────────────
print("\n── Ordens de Serviço ───────────────────────────────────")

r = client.get("/api/v1/ordens-servico", headers=HDR_REC)
check("GET /ordens-servico → 200", r.status_code == 200)
check("2 OS mock presentes", r.json()["total"] >= 2)

r = client.get("/api/v1/ordens-servico?estado=PENDENTE", headers=HDR_REC)
check("GET /ordens-servico?estado=PENDENTE → só pendentes", all(o["estado"] == "PENDENTE" for o in r.json()["data"]))

r = client.get("/api/v1/ordens-servico/1", headers=HDR_MEC)
check("GET /ordens-servico/1 (MECANICO) → 200", r.status_code == 200)
d = r.json()["data"]
check("detalhe tem cliente, trotinete, mecanico", all(k in d for k in ("cliente", "trotinete", "mecanico")))
check("subtotal_pecas e valor_estimado_total presentes", "subtotal_pecas" in d and "valor_estimado_total" in d)

# GET OS inexistente
r = client.get("/api/v1/ordens-servico/999", headers=HDR_REC)
check("GET /ordens-servico/999 → 404", r.status_code == 404)

# Criar OS
nova_os = {
    "trotinete_id": 1,
    "loja_id": 1,
    "mecanico_id": 4,
    "descricao_problema": "OS de teste criada pelo smoke test.",
    "prioridade": "NORMAL",
    "preco_servico": 20.00,
}
r = client.post("/api/v1/ordens-servico", json=nova_os, headers=HDR_REC)
check("POST /ordens-servico → 201", r.status_code == 201)
ID_OS_NOVA = r.json()["data"]["id"]
check("estado inicial = PENDENTE", r.json()["data"]["estado"] == "PENDENTE")

# MECANICO não pode criar OS
r = client.post("/api/v1/ordens-servico", json=nova_os, headers=HDR_MEC)
check("MECANICO POST /ordens-servico → 403", r.status_code == 403)

# Transição válida: PENDENTE → EM_DIAGNOSTICO (MECANICO pode)
r = client.patch(f"/api/v1/ordens-servico/{ID_OS_NOVA}/estado",
    json={"novo_estado": "EM_DIAGNOSTICO"},
    headers=HDR_MEC)
check("PATCH estado PENDENTE→EM_DIAGNOSTICO (MECANICO) → 200", r.status_code == 200)
check("estado_anterior = PENDENTE", r.json()["data"]["estado_anterior"] == "PENDENTE")

# Transição inválida: EM_DIAGNOSTICO → CONCLUIDA
r = client.patch(f"/api/v1/ordens-servico/{ID_OS_NOVA}/estado",
    json={"novo_estado": "CONCLUIDA"},
    headers=HDR_MEC)
check("Transição inválida → 409 INVALID_STATE_TRANSITION", r.status_code == 409)

# Avançar até EM_REPARACAO para poder adicionar peças
client.patch(f"/api/v1/ordens-servico/{ID_OS_NOVA}/estado",
    json={"novo_estado": "AGUARDA_APROVACAO"}, headers=HDR_MEC)
client.patch(f"/api/v1/ordens-servico/{ID_OS_NOVA}/estado",
    json={"novo_estado": "EM_REPARACAO"}, headers=HDR_REC)

# Adicionar peça
r = client.post(f"/api/v1/ordens-servico/{ID_OS_NOVA}/pecas",
    json={"peca_id": 1, "quantidade": 1},
    headers=HDR_MEC)
check("POST /ordens-servico/{id}/pecas → 201", r.status_code == 201)
check("preco_venda_unitario presente (snapshot)", "preco_venda_unitario" in r.json()["data"])
check("preco_custo NÃO na resposta de peça aplicada", "preco_custo" not in r.json()["data"])

# Registo de tempos
r = client.post(f"/api/v1/ordens-servico/{ID_OS_NOVA}/tempos/iniciar", headers=HDR_MEC)
check("POST /tempos/iniciar → 200", r.status_code == 200)

r = client.post(f"/api/v1/ordens-servico/{ID_OS_NOVA}/tempos/iniciar", headers=HDR_MEC)
check("Iniciar tempo já iniciado → 409", r.status_code == 409)

r = client.post(f"/api/v1/ordens-servico/{ID_OS_NOVA}/tempos/parar", headers=HDR_MEC)
check("POST /tempos/parar → 200", r.status_code == 200)
check("tempo_total_acumulado_minutos presente", "tempo_total_acumulado_minutos" in r.json()["data"])

# Verificar valor_estimado_total na OS após peça adicionada
r = client.get(f"/api/v1/ordens-servico/{ID_OS_NOVA}", headers=HDR_REC)
d = r.json()["data"]
check("subtotal_pecas > 0 após adicionar peça", d["subtotal_pecas"] > 0)
check("valor_estimado_total = preco_servico + subtotal_pecas",
    abs(d["valor_estimado_total"] - (d["preco_servico"] + d["subtotal_pecas"])) < 0.01)


# ─────────────────────────────────────────────────────────────────
print("\n── Resumo ──────────────────────────────────────────────")
total = len(results)
passed = sum(results)
failed = total - passed
print(f"\n  Total: {total}  |  {PASS} {passed}  |  {FAIL} {failed}\n")
if failed > 0:
    raise SystemExit(1)
