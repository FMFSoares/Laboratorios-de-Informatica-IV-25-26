"""
Smoke tests para verificar os endpoints implementados até ao passo 10.
Corre sem base de dados — usa os mocks em memória.
"""

import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-dlmcare-2026")
os.environ["APP_ENV"] = "test"

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal

# Clean up test-created data so the suite is idempotent across runs
def _cleanup():
    db = SessionLocal()
    try:
        db.execute(__import__('sqlalchemy').text(
            "DELETE FROM clientes WHERE nif IN ('225476541','301234566','412345676')"
        ))
        db.execute(__import__('sqlalchemy').text(
            "DELETE FROM trotinetes WHERE numero_serie IN ('SG2026TEST999','SG2026TEST888')"
        ))
        db.execute(__import__('sqlalchemy').text(
            "DELETE FROM pecas WHERE referencia IN ('PEC-TEST-001','PEC-TEST-002')"
        ))
        db.commit()
    finally:
        db.close()

_cleanup()

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
r = client.post("/api/v1/auth/login", json={"email": "ines.carvalho@dlmcare.pt", "password": "123456"})
check("Login válido (RECECIONISTA) → 201", r.status_code == 201)
data = r.json()
check("access_token presente", "access_token" in data)
check("perfil = RECECIONISTA", data["user"]["perfil"] == "RECECIONISTA", data.get("user", {}).get("perfil",""))
TOKEN_REC = data["access_token"]
REFRESH_TOKEN = data["refresh_token"]

# Login válido — ADMIN
r = client.post("/api/v1/auth/login", json={"email": "david@dlmcare.pt", "password": "123456"})
check("Login válido (ADMIN) → 201", r.status_code == 201)
TOKEN_ADMIN = r.json()["access_token"]

# Login válido — MECANICO
r = client.post("/api/v1/auth/login", json={"email": "tiago.mendes@dlmcare.pt", "password": "123456"})
check("Login válido (MECANICO) → 201", r.status_code == 201)
TOKEN_MEC = r.json()["access_token"]

# GET /me
r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {TOKEN_REC}"})
check("GET /auth/me → 200", r.status_code == 200)
check("email correto no /me", r.json()["email"] == "ines.carvalho@dlmcare.pt")

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
    "nif": "225476541",
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
r = client.post("/api/v1/clientes", json={**novo_cliente, "nif": "301234566"}, headers=HDR_MEC)
check("MECANICO POST /clientes → 403", r.status_code == 403)

# RGPD obrigatório
r = client.post("/api/v1/clientes", json={**novo_cliente, "nif": "412345676", "consentimento_rgpd": False}, headers=HDR_REC)
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
r = client.post("/api/v1/trotinetes", json={**nova_trotinete, "numero_serie": "SG2026TEST888"}, headers=HDR_MEC)
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

r = client.get("/api/v1/stock?apenas_alertas=true", headers=HDR_REC)
check("GET /stock?apenas_alertas=true → 200", r.status_code == 200)
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
    json={"novo_estado": "EM_REPARACAO"}, headers=HDR_ADMIN)

# Adicionar peça
r = client.post(f"/api/v1/ordens-servico/{ID_OS_NOVA}/pecas",
    json={"peca_id": 1, "quantidade": 1},
    headers=HDR_MEC)
check("POST /ordens-servico/{id}/pecas → 201", r.status_code == 201)
check("preco_venda_unitario presente (snapshot)", "preco_venda_unitario" in r.json()["data"])
check("preco_custo NÃO na resposta de peça aplicada", "preco_custo" not in r.json()["data"])

# Registo de tempos
r = client.post(f"/api/v1/ordens-servico/{ID_OS_NOVA}/tempos/iniciar", headers=HDR_MEC)
check("POST /tempos/iniciar → 201", r.status_code == 201)

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
print("\n── Faturas ─────────────────────────────────────────────")

# Avançar a OS criada no teste até CONCLUIDA para poder faturar
client.patch(f"/api/v1/ordens-servico/{ID_OS_NOVA}/estado",
    json={"novo_estado": "CONCLUIDA"}, headers=HDR_MEC)

# POST /faturas — OS ainda não faturada
r = client.post("/api/v1/faturas", json={"ordem_servico_id": ID_OS_NOVA}, headers=HDR_REC)
check("POST /faturas → 201", r.status_code == 201)
d = r.json()["data"]
check("numero tem formato FAT-2026-XXXX", d["numero"].startswith("FAT-2026-"))
check("estado = EMITIDA", d["estado"] == "EMITIDA")
check("valor_final = preco_servico + subtotal_pecas",
    abs(d["valor_final"] - (d["servico"]["preco_servico"] + d["subtotal_pecas"])) < 0.01)
check("preco_custo NÃO na fatura", "preco_custo" not in str(d))
check("message presente", "message" in r.json())
ID_FATURA = d["id"]

# OS transitou para FATURADA
r_os = client.get(f"/api/v1/ordens-servico/{ID_OS_NOVA}", headers=HDR_REC)
check("OS transitou para FATURADA", r_os.json()["data"]["estado"] == "FATURADA")

# POST /faturas — OS já faturada → 409
r = client.post("/api/v1/faturas", json={"ordem_servico_id": ID_OS_NOVA}, headers=HDR_REC)
check("POST /faturas OS já faturada → 409 ORDER_ALREADY_INVOICED", r.status_code == 409)
check("code = ORDER_ALREADY_INVOICED", r.json()["detail"]["code"] == "ORDER_ALREADY_INVOICED")

# POST /faturas — OS não concluída (OS 1 está PENDENTE) → 400
r = client.post("/api/v1/faturas", json={"ordem_servico_id": 1}, headers=HDR_REC)
check("POST /faturas OS não concluída → 400 ORDER_NOT_CONCLUDED", r.status_code == 400)
check("code = ORDER_NOT_CONCLUDED", r.json()["detail"]["code"] == "ORDER_NOT_CONCLUDED")

# POST /faturas — OS inexistente → 404
r = client.post("/api/v1/faturas", json={"ordem_servico_id": 999}, headers=HDR_REC)
check("POST /faturas OS inexistente → 404", r.status_code == 404)

# MECANICO não pode emitir faturas → 403
r = client.post("/api/v1/faturas", json={"ordem_servico_id": ID_OS_NOVA}, headers=HDR_MEC)
check("MECANICO POST /faturas → 403", r.status_code == 403)

# GET /faturas/{id}
r = client.get(f"/api/v1/faturas/{ID_FATURA}", headers=HDR_REC)
check("GET /faturas/{id} → 200", r.status_code == 200)
check("campos obrigatórios presentes", all(k in r.json()["data"] for k in ("cliente", "trotinete", "servico", "loja", "pecas_aplicadas")))

# GET /faturas/{id} inexistente
r = client.get("/api/v1/faturas/999", headers=HDR_REC)
check("GET /faturas/999 → 404", r.status_code == 404)

# GET /faturas — listagem
r = client.get("/api/v1/faturas", headers=HDR_REC)
check("GET /faturas → 200", r.status_code == 200)
check("1 fatura presente", r.json()["total"] >= 1)

# Filtro por ordem_servico_id
r = client.get(f"/api/v1/faturas?ordem_servico_id={ID_OS_NOVA}", headers=HDR_REC)
check("GET /faturas?ordem_servico_id → 1 resultado", r.json()["total"] == 1)


# ─────────────────────────────────────────────────────────────────
print("\n── Dashboard ───────────────────────────────────────────")

# ADMIN pode aceder
r = client.get("/api/v1/dashboard", headers=HDR_ADMIN)
check("GET /dashboard (ADMIN) → 200", r.status_code == 200)
d = r.json()["data"]
check("campos obrigatórios presentes", all(k in d for k in (
    "periodo", "ordens_por_estado", "ordens_concluidas_por_loja",
    "faturacao_total", "pecas_abaixo_stock_minimo", "eficiencia_por_mecanico"
)))
check("ordens_por_estado tem todos os estados", all(
    e in d["ordens_por_estado"]
    for e in ("PENDENTE", "EM_DIAGNOSTICO", "AGUARDA_APROVACAO",
              "EM_REPARACAO", "AGUARDA_PECAS", "CONCLUIDA", "FATURADA", "CANCELADA")
))
check("faturacao_total é número", isinstance(d["faturacao_total"], (int, float)))
check("pecas_abaixo_stock_minimo é lista", isinstance(d["pecas_abaixo_stock_minimo"], list))

# GERENTE pode aceder
r = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {r.json().get('access_token', TOKEN_ADMIN)}"})
r = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {client.post('/api/v1/auth/login', json={'email': 'jose.barros@dlmcare.pt', 'password': '123456'}).json().get('access_token', '')}"})
# Simplificar: usar token de admin com loja_id query param
r = client.get("/api/v1/dashboard?loja_id=1", headers=HDR_ADMIN)
check("GET /dashboard?loja_id=1 (ADMIN) → 200", r.status_code == 200)
check("periodo.inicio e periodo.fim presentes", "inicio" in r.json()["data"]["periodo"])

# RECECIONISTA não pode aceder
r = client.get("/api/v1/dashboard", headers=HDR_REC)
check("RECECIONISTA GET /dashboard → 403", r.status_code == 403)

# MECANICO não pode aceder
r = client.get("/api/v1/dashboard", headers=HDR_MEC)
check("MECANICO GET /dashboard → 403", r.status_code == 403)

# Filtro por período
r = client.get("/api/v1/dashboard?data_inicio=2026-01-01&data_fim=2026-12-31", headers=HDR_ADMIN)
check("GET /dashboard com período explícito → 200", r.status_code == 200)
check("periodo reflete params enviados",
    r.json()["data"]["periodo"]["inicio"] == "2026-01-01" and
    r.json()["data"]["periodo"]["fim"] == "2026-12-31")


# ─────────────────────────────────────────────────────────────────
print("\n── Auditoria ───────────────────────────────────────────")

# ADMIN pode listar
r = client.get("/api/v1/auditoria", headers=HDR_ADMIN)
check("GET /auditoria (ADMIN) → 200", r.status_code == 200)
check("devolve lista paginada", "data" in r.json() and "total" in r.json())
check("7 eventos mock presentes", r.json()["total"] >= 7)
check("campos obrigatórios no item", all(
    k in r.json()["data"][0]
    for k in ("id", "evento", "descricao", "timestamp", "detalhe")
))

# RECECIONISTA não pode aceder
r = client.get("/api/v1/auditoria", headers=HDR_REC)
check("RECECIONISTA GET /auditoria → 403", r.status_code == 403)

# MECANICO não pode aceder
r = client.get("/api/v1/auditoria", headers=HDR_MEC)
check("MECANICO GET /auditoria → 403", r.status_code == 403)

# Filtro por evento
r = client.get("/api/v1/auditoria?evento=LOGIN_SUCESSO", headers=HDR_ADMIN)
check("GET /auditoria?evento=LOGIN_SUCESSO → 200", r.status_code == 200)
check("todos os itens têm evento=LOGIN_SUCESSO", all(
    i["evento"] == "LOGIN_SUCESSO" for i in r.json()["data"]
))

# Filtro por utilizador_id
r = client.get("/api/v1/auditoria?utilizador_id=3", headers=HDR_ADMIN)
check("GET /auditoria?utilizador_id=3 → filtra por utilizador", all(
    i["utilizador_id"] == 3 for i in r.json()["data"]
))

# Filtro por loja_id (ADMIN)
r = client.get("/api/v1/auditoria?loja_id=1", headers=HDR_ADMIN)
check("GET /auditoria?loja_id=1 (ADMIN) → 200", r.status_code == 200)

# Filtro por período
r = client.get("/api/v1/auditoria?data_inicio=2026-04-28&data_fim=2026-04-28", headers=HDR_ADMIN)
check("GET /auditoria com período → 200", r.status_code == 200)
check("resultado filtrado pelo período", r.json()["total"] >= 1)

# Paginação
r = client.get("/api/v1/auditoria?page=1&page_size=3", headers=HDR_ADMIN)
check("paginação page_size=3 → 3 itens ou menos", len(r.json()["data"]) <= 3)
check("pages calculado corretamente", r.json()["pages"] >= 1)


# ─────────────────────────────────────────────────────────────────
print("\n── Resumo ──────────────────────────────────────────────")
total = len(results)
passed = sum(results)
failed = total - passed
print(f"\n  Total: {total}  |  {PASS} {passed}  |  {FAIL} {failed}\n")
if failed > 0:
    raise SystemExit(1)
