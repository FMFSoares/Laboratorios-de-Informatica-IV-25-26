# DLMCare

Sistema de gestão para uma cadeia de oficinas de reparação de trotinetes elétricas (Lisboa, Porto, Braga).

Desenvolvido no âmbito da UC de Laboratórios de Informática IV — Universidade do Minho, 2025/2026.

| Nº | Nome |
|---|---|
| A107369 | Pedro Ribeiro Ferreira |
| A107335 | Rodrigo de Sousa Campos Pacheco da Rocha |
| A107325 | David Lopes Machado |
| A106901 | Francisco Miguel Fernandes Soares |

## Stack

- **Backend:** Python 3.13 + FastAPI
- **Base de dados:** MySQL 8.0
- **Frontend:** Vue.js 3 + Vite

---

## Setup (máquina nova)

### Pré-requisitos

- Python 3.13+
- Node.js 18+ e npm
- MySQL 8.0+ (ou Docker)

### 1. Clonar o repositório

```bash
git clone https://github.com/FMFSoares/Laboratorios-de-Informatica-IV-25-26.git
cd Laboratorios-de-Informatica-IV-25-26
```

### 2. Variáveis de ambiente

```bash
cp .env.example backend/.env
# Editar backend/.env com os dados da tua BD local e gerar o JWT_SECRET_KEY:
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 4. Base de dados

```bash
# Iniciar MySQL e criar o schema (só uma vez)
sudo systemctl start mysql
sudo mysql
```
```sql
source /caminho/para/o/projeto/database/init.sql
EXIT;
```

```bash
# Aplicar migrations (criar as tabelas)
cd backend && source venv/bin/activate
alembic upgrade head
cd ..
```

### 5. Frontend

```bash
cd frontend
npm install
cd ..
```

---

## Correr o projeto

Abrir **3 terminais**:

```bash
# Terminal 1 — Base de dados
sudo systemctl start mysql

# Terminal 2 — Backend  (http://localhost:8000)
cd backend && source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 3 — Frontend  (http://localhost:5173)
cd frontend && npm run dev
```

Confirmar que está tudo a funcionar:
- `http://localhost:8000/health` → `{"status": "ok", ...}`
- `http://localhost:8000/docs` → documentação interativa da API
- `http://localhost:5173` → frontend

---

## Quando há atualizações do grupo

```bash
git checkout develop
git pull origin develop

# Se houver migrations novas:
cd backend && source venv/bin/activate && alembic upgrade head

# Se houver dependências novas:
pip install -r requirements.txt   # Python
cd ../frontend && npm install     # Node
```

---

## Documentação

| Ficheiro | Conteúdo |
|---|---|
| `docs/setup_inicial.txt` | Explicação detalhada de todos os ficheiros criados no setup |
| `docs/git_branching.txt` | Guia de branching strategy e comandos Git |
