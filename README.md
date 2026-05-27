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

## Setup numa máquina nova

### Pré-requisitos

Instala estas ferramentas antes de começar:

- **Python 3.13+** — https://www.python.org/downloads/
- **Node.js 18+ e npm** — https://nodejs.org/
- **MySQL 8.0+** — https://dev.mysql.com/downloads/mysql/

---

### 1. Clonar o repositório

```bash
git clone https://github.com/FMFSoares/Laboratorios-de-Informatica-IV-25-26.git
cd Laboratorios-de-Informatica-IV-25-26
```

---

### 2. Criar a base de dados MySQL

Abre o terminal MySQL como root:

```bash
# Linux/Mac:
sudo mysql

# Windows (se o MySQL estiver no PATH):
mysql -u root -p
```

Dentro do MySQL, corre o script de inicialização (substitui o caminho completo):

```sql
source /caminho/completo/para/database/init.sql;
EXIT;
```

Exemplo no Windows:
```sql
source C:/Users/TeuNome/Laboratorios-de-Informatica-IV-25-26/database/init.sql;
EXIT;
```

Isto cria a base de dados `dlmcare` e o utilizador `dlmcare_user` com password `DlmCare_2026!`.

---

### 3. Configurar as variáveis de ambiente do backend

Copia o ficheiro de exemplo:

```bash
cp .env.example backend/.env
```

Abre `backend/.env` e preenche-o assim (copia e cola diretamente):

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=dlmcare
DB_USER=dlmcare_user
DB_PASSWORD=DlmCare_2026!
DATABASE_URL=mysql+pymysql://dlmcare_user:DlmCare_2026!@localhost:3306/dlmcare

JWT_SECRET_KEY=GERA_UM_ABAIXO
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_DAYS=7

APP_ENV=development
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:4173

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=
```

> **Atenção:** Escreve o `DATABASE_URL` como uma string completa. O python-dotenv **não** expande variáveis `${DB_USER}` como o bash faz.

Para o `JWT_SECRET_KEY`, gera uma chave aleatória:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Cola o resultado no `.env` como valor de `JWT_SECRET_KEY`.

---

### 4. Instalar dependências do backend

```bash
cd backend
python3 -m venv venv
```

Ativar o ambiente virtual:
```bash
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

Instalar os pacotes:
```bash
pip install -r requirements.txt
```

---

### 5. Criar as tabelas (migrações)

Com o venv ainda ativo e dentro da pasta `backend`:

```bash
alembic upgrade head
```

Deves ver algo como `Running upgrade ... -> ..., ...` para cada migração. Se der erro de ligação, confirma que o MySQL está a correr e que o `DATABASE_URL` no `.env` está correto.

---

### 6. Popular a base de dados com dados de teste

Sai da pasta backend e corre os scripts de seed:

```bash
cd ..
mysql -u dlmcare_user -pDlmCare_2026! dlmcare < database/seed.sql
mysql -u dlmcare_user -pDlmCare_2026! dlmcare < database/demo_data.sql
```

> No Windows, usa o MySQL Shell ou o MySQL Workbench para importar os ficheiros manualmente se o comando acima não funcionar.

---

### 7. Instalar dependências do frontend

```bash
cd frontend
npm install
```

Criar o ficheiro de configuração do frontend:

```bash
# Linux/Mac:
echo "VITE_API_BASE_URL=http://localhost:8000/api/v1" > .env.local

# Windows (PowerShell):
echo "VITE_API_BASE_URL=http://localhost:8000/api/v1" | Out-File -Encoding utf8 .env.local
```

```bash
cd ..
```

---

### 8. Correr o projeto

Precisas de **3 terminais em simultâneo**:

**Terminal 1 — MySQL** (se não estiver já a correr)
```bash
# Linux:
sudo systemctl start mysql

# Mac (Homebrew):
brew services start mysql

# Windows: abre o MySQL Workbench ou usa o Windows Services
```

**Terminal 2 — Backend** (porta 8000)
```bash
cd backend
source venv/bin/activate   # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 3 — Frontend** (porta 5173)
```bash
cd frontend
npm run dev
```

---

### 9. Verificar que está tudo a funcionar

Abre no browser:

- `http://localhost:5173` → aplicação frontend
- `http://localhost:8000/docs` → documentação interativa da API (Swagger)

**Login de admin para testes:**
- Email: `david@dlmcare.pt`
- Password: `123456`

---

## Quando há atualizações do grupo

```bash
git pull origin master

# Se houver migrações novas:
cd backend && source venv/bin/activate && alembic upgrade head

# Se houver dependências novas no backend:
pip install -r requirements.txt

# Se houver dependências novas no frontend:
cd ../frontend && npm install
```

---

## Documentação

| Ficheiro | Conteúdo |
|---|---|
| `docs/setup_inicial.txt` | Explicação detalhada de todos os ficheiros criados no setup |
| `docs/git_branching.txt` | Guia de branching strategy e comandos Git |
