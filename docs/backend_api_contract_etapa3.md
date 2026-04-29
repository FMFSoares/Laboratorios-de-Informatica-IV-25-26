# DLMCare — Contrato da API Backend (Etapa 3)

**Projeto:** DLMCare — Sistema de gestão para uma cadeia de oficinas de reparação de trotinetes  
**Etapa:** 3 — Implementação e Desenvolvimento Assistido por LLM  
**Última atualização:** 2026-04-28  
**Responsável backend:** Francisco Soares (A106901)

---

## Índice

1. [Introdução](#1-introdução)
2. [Convenções gerais da API](#2-convenções-gerais-da-api)
3. [Perfis de utilizador e permissões](#3-perfis-de-utilizador-e-permissões)
4. [Autenticação](#4-autenticação)
5. [Clientes](#5-clientes)
6. [Trotinetes](#6-trotinetes)
7. [Peças](#7-peças)
8. [Stock](#8-stock)
9. [Ordens de Serviço](#9-ordens-de-serviço)
10. [Faturação](#10-faturação)
11. [Dashboard](#11-dashboard)
12. [Auditoria](#12-auditoria)
13. [Tabela-resumo final](#13-tabela-resumo-final)
14. [Notas para implementação backend na Etapa 3](#14-notas-para-implementação-backend-na-etapa-3)
15. [Fora de âmbito](#15-fora-de-âmbito)

---

## 1. Introdução

### Objetivo do contrato

Este documento define o **contrato da API REST** do backend DLMCare para a Etapa 3. Serve como referência única e partilhada entre o backend (este trabalho), o frontend (outro elemento do grupo) e quem implementar a camada de persistência.

Um contrato de API estabelece, sem ambiguidade:
- quais os endpoints existentes
- o que cada um recebe e devolve
- quais as regras de negócio aplicadas
- quais as permissões exigidas
- qual o estado de implementação de cada módulo

### Papel deste contrato na Etapa 3

Na Etapa 3, o objetivo é implementar o backend aplicacional de forma incremental. Isto significa que:

- Os endpoints ficam funcionais e testáveis o mais cedo possível.
- A lógica de negócio é implementada em services que, numa primeira fase, podem usar dados em memória (mockados).
- A integração real com a base de dados é adicionada posteriormente, sem alterar os contratos dos endpoints.

O frontend pode começar a ser desenvolvido em paralelo, apontando para esta API, desde que o contrato seja respeitado.

### Separação entre backend aplicacional e persistência

Este projeto separa explicitamente duas responsabilidades:

| Responsabilidade | Quem trata | Etapa |
|---|---|---|
| Esquema SQL (tabelas, relações, índices) | Outro elemento do grupo | Paralelo |
| Modelos ORM SQLAlchemy | Outro elemento do grupo | Paralelo |
| Migrations Alembic | Outro elemento do grupo | Paralelo |
| Routers FastAPI, schemas Pydantic, services, auth, permissões | Francisco Soares | Etapa 3 |
| Frontend Vue.js | Outro elemento do grupo | Etapa 3 |

### Integração com BD posterior

Enquanto a persistência não estiver disponível, os services serão implementados com dados mockados em memória. Isto **não bloqueia** o desenvolvimento do backend:

- Os routers, schemas e validações funcionam completamente.
- Os testes com `TestClient` do FastAPI funcionam.
- O frontend pode consumir a API com dados de teste realistas.
- Quando os repositories reais (com queries à BD) estiverem prontos, substituem o mock sem alterar routers nem schemas.

> **Convenção:** Ao longo deste documento, a nota `[pendente de integração com BD]` indica que um comportamento depende da persistência real, mas que existe uma versão mockada funcional na Etapa 3.

---

## 2. Convenções gerais da API

### Prefixo base

Todos os endpoints de negócio usam o prefixo:

```
/api/v1
```

O endpoint `/health` é o único fora deste prefixo (já implementado).

### Formato

- Todas as respostas são em **JSON** (`Content-Type: application/json`).
- Datas e timestamps no formato **ISO 8601**: `"2026-04-28T14:30:00Z"`.
- Identificadores são **inteiros** (`int`) por defeito, compatíveis com chaves primárias MySQL.
- Campos opcionais ausentes são devolvidos como `null`, não omitidos.

### Códigos HTTP utilizados

| Código | Significado | Quando usar |
|---|---|---|
| `200 OK` | Sucesso geral | GET, PUT, PATCH com resposta |
| `201 Created` | Recurso criado | POST bem-sucedido |
| `204 No Content` | Sucesso sem corpo | DELETE, PATCH sem resposta |
| `400 Bad Request` | Dados inválidos | Validação Pydantic falhou, regra de negócio violada |
| `401 Unauthorized` | Não autenticado | Token ausente, expirado ou inválido |
| `403 Forbidden` | Sem permissão | Autenticado mas perfil não autorizado, ou loja errada |
| `404 Not Found` | Recurso inexistente | ID não encontrado |
| `409 Conflict` | Conflito de estado | Recurso duplicado, transição de estado inválida |
| `422 Unprocessable Entity` | Erro de schema | FastAPI / Pydantic (automático) |
| `500 Internal Server Error` | Erro inesperado | Exceção não tratada |

### Formato padrão de sucesso

```json
{
  "data": { ... },
  "message": "Operação realizada com sucesso."
}
```

Para listas paginadas:

```json
{
  "data": [ ... ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

### Formato padrão de erro

```json
{
  "detail": "Mensagem de erro legível para o utilizador.",
  "code": "CODIGO_ERRO_INTERNO"
}
```

Exemplos de `code`:

| `code` | Situação |
|---|---|
| `INVALID_CREDENTIALS` | Login com credenciais erradas |
| `TOKEN_EXPIRED` | JWT expirado |
| `PERMISSION_DENIED` | Perfil sem acesso |
| `LOJA_MISMATCH` | Utilizador a aceder a dados de outra loja |
| `RESOURCE_NOT_FOUND` | ID não encontrado |
| `DUPLICATE_ENTRY` | Registo duplicado (ex: NIF, nº série) |
| `INVALID_STATE_TRANSITION` | Transição de estado não permitida |
| `ORDER_NOT_CONCLUDED` | Tentativa de faturar ordem não concluída |
| `ORDER_ALREADY_INVOICED` | Tentativa de emitir segunda fatura |
| `INSUFFICIENT_STOCK` | Stock insuficiente para transferência |
| `VALIDATION_ERROR` | Dados inválidos no body |

### Paginação

Os endpoints de listagem suportam paginação por query params:

| Param | Tipo | Padrão | Descrição |
|---|---|---|---|
| `page` | int | `1` | Página a devolver (base 1) |
| `page_size` | int | `20` | Resultados por página (máx 100) |

### Autenticação

Todos os endpoints (exceto `POST /api/v1/auth/login`) exigem o header:

```
Authorization: Bearer <access_token>
```

O token é um JWT assinado com `HS256`. A ausência ou invalidade do token devolve `401`.

---

## 3. Perfis de utilizador e permissões

### Perfis existentes

| Perfil | Descrição | `loja_id` |
|---|---|---|
| `ADMINISTRADOR` | Acesso global a toda a rede de lojas | `null` |
| `GERENTE_LOJA` | Gere operações e relatórios da sua loja | obrigatório |
| `RECECIONISTA` | Regista clientes, trotinetes e ordens de serviço | obrigatório |
| `MECANICO` | Executa diagnósticos e reparações | obrigatório |

### Regras de acesso multi-loja

- `ADMINISTRADOR` acede a **todos os dados** de todas as lojas sem restrição.
- `GERENTE_LOJA`, `RECECIONISTA` e `MECANICO` apenas veem e operam **dados da sua própria `loja_id`**.
- Qualquer tentativa de acesso a dados de outra loja por um utilizador sem ser ADMINISTRADOR devolve `403` com `code: LOJA_MISMATCH`.
- Esta regra é aplicada nas **FastAPI dependencies**, de forma centralizada, e não endpoint a endpoint.

### Filtro automático por loja

Em endpoints de listagem, o filtro `loja_id` é:
- Opcional para `ADMINISTRADOR` (se omitido, devolve dados de todas as lojas).
- Ignorado para os restantes perfis: o sistema usa sempre a `loja_id` do utilizador autenticado.

### Implementação nas dependencies

As seguintes dependencies serão criadas em `auth/dependencies.py`:

| Dependency | Descrição |
|---|---|
| `get_current_user` | Valida o JWT e devolve o utilizador autenticado |
| `require_roles(*perfis)` | Garante que o utilizador tem um dos perfis indicados |
| `get_loja_context` | Devolve a `loja_id` efectiva (da loja do user, ou do query param se ADMIN) |

### Matriz de permissões por módulo

| Módulo | ADMINISTRADOR | GERENTE_LOJA | RECECIONISTA | MECANICO |
|---|---|---|---|---|
| Auth (login, me) | ✓ | ✓ | ✓ | ✓ |
| Clientes (leitura) | ✓ | ✓ | ✓ | ✓ |
| Clientes (escrita) | ✓ | ✓ | ✓ | — |
| Trotinetes | ✓ | ✓ | ✓ | leitura |
| Peças (leitura) | ✓ | ✓ | ✓ | ✓ |
| Peças (escrita) | ✓ | ✓ | — | — |
| Stock (leitura) | ✓ | ✓ | ✓ | ✓ |
| Stock (entradas/transferências) | ✓ | ✓ | — | — |
| Ordens de Serviço (criar) | ✓ | ✓ | ✓ | — |
| Ordens de Serviço (reparação) | ✓ | ✓ | — | ✓ |
| Ordens de Serviço (transição estado) | ✓ | ✓ | parcial | parcial |
| Faturação | ✓ | ✓ | ✓ | — |
| Dashboard | ✓ | ✓ | — | — |
| Auditoria | ✓ | ✓ | — | — |
| Utilizadores (gestão) | ✓ | — | — | — |

> Transições de estado são parciais: RECECIONISTA pode criar/cancelar ordens; MECANICO pode avançar estados de diagnóstico e reparação. Ver secção 9.

---

## 4. Autenticação

**Service associado:** `services/auth_service.py`  
**Router:** `routers/auth.py`  
**Schemas:** `schemas/auth.py`

### Decisões de implementação para a Etapa 3

- O login usa uma lista mockada de utilizadores em memória `[pendente de integração com BD]`.
- O refresh token é **stateless** (JWT puro). Não existe tabela de refresh tokens.
- Um refresh token expirado ou inválido obriga a novo login.

---

### POST /api/v1/auth/login

**Descrição:** Autentica um utilizador com email e password. Devolve um par de tokens JWT.  
**Autenticação exigida:** Não  
**Perfis autorizados:** Todos (qualquer utilizador registado)  
**Estado:** Mockado na Etapa 3 `[pendente de integração com BD]`

**Request body:**
```json
{
  "email": "ana.lisboa@dlmcare.pt",
  "password": "password123"
}
```

**Response `201`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "id": 2,
    "nome": "Ana Rececionista",
    "email": "ana.lisboa@dlmcare.pt",
    "perfil": "RECECIONISTA",
    "loja_id": 1,
    "loja_nome": "DLMCare Lisboa"
  }
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `401` | `INVALID_CREDENTIALS` | Email não existe ou password incorreta |
| `403` | `ACCOUNT_INACTIVE` | Utilizador com `ativo = false` |
| `422` | — | Body inválido (automático Pydantic) |

---

### POST /api/v1/auth/refresh

**Descrição:** Troca um refresh token válido por um novo par de tokens.  
**Autenticação exigida:** Não (usa o refresh token no body)  
**Perfis autorizados:** Todos  
**Estado:** Implementado como JWT stateless

**Request body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response `200`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 28800
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `401` | `TOKEN_EXPIRED` | Refresh token expirado |
| `401` | `TOKEN_INVALID` | Token malformado ou assinatura inválida |

---

### GET /api/v1/auth/me

**Descrição:** Devolve os dados do utilizador autenticado com base no access token.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** Todos  
**Estado:** Implementado (sem dependência de BD se o JWT contiver os dados do utilizador)

**Response `200`:**
```json
{
  "id": 2,
  "nome": "Ana Rececionista",
  "email": "ana.lisboa@dlmcare.pt",
  "perfil": "RECECIONISTA",
  "loja_id": 1,
  "loja_nome": "DLMCare Lisboa",
  "ativo": true
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `401` | `TOKEN_EXPIRED` | Token expirado |
| `401` | `TOKEN_INVALID` | Token inválido |

---

## 5. Clientes

**Service associado:** `services/cliente_service.py`  
**Router:** `routers/clientes.py`  
**Schemas:** `schemas/cliente.py`  
**Estado geral:** Mockado na Etapa 3 `[pendente de integração com BD]`

### Validações obrigatórias

| Campo | Regra |
|---|---|
| `nif` | 9 dígitos numéricos, único no sistema |
| `telemovel` | 9 dígitos, começa por 9, formato PT |
| `email` | Formato RFC 5322 válido, quando fornecido |
| `consentimento_rgpd` | Obrigatório `true` no momento do registo |

---

### GET /api/v1/clientes

**Descrição:** Lista clientes com filtro opcional por NIF ou telemóvel.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA, MECANICO  
**Filtro de loja:** Automático (exceto ADMINISTRADOR)

**Query params:**

| Param | Tipo | Descrição |
|---|---|---|
| `query` | string | Pesquisa por NIF ou telemóvel (exact match) |
| `page` | int | Página (padrão: 1) |
| `page_size` | int | Resultados por página (padrão: 20) |

**Response `200`:**
```json
{
  "data": [
    {
      "id": 1,
      "nome": "João Silva",
      "nif": "123456789",
      "telemovel": "912345678",
      "email": "joao.silva@email.com",
      "morada": "Rua das Flores 10, Lisboa",
      "consentimento_rgpd": true,
      "data_registo": "2026-04-01T10:00:00Z",
      "loja_id": 1
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

---

### POST /api/v1/clientes

**Descrição:** Regista um novo cliente.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA

**Request body:**
```json
{
  "nome": "João Silva",
  "nif": "123456789",
  "telemovel": "912345678",
  "email": "joao.silva@email.com",
  "morada": "Rua das Flores 10, Lisboa",
  "consentimento_rgpd": true
}
```

**Response `201`:**
```json
{
  "data": {
    "id": 1,
    "nome": "João Silva",
    "nif": "123456789",
    "telemovel": "912345678",
    "email": "joao.silva@email.com",
    "morada": "Rua das Flores 10, Lisboa",
    "consentimento_rgpd": true,
    "data_registo": "2026-04-28T14:00:00Z",
    "loja_id": 1
  },
  "message": "Cliente registado com sucesso."
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `400` | `RGPD_CONSENT_REQUIRED` | `consentimento_rgpd` é `false` ou ausente |
| `409` | `DUPLICATE_ENTRY` | NIF já registado no sistema |
| `422` | — | NIF com formato inválido, telemóvel inválido, email inválido |

---

### GET /api/v1/clientes/{id}

**Descrição:** Devolve os dados completos de um cliente pelo ID.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA, MECANICO

**Response `200`:**
```json
{
  "data": {
    "id": 1,
    "nome": "João Silva",
    "nif": "123456789",
    "telemovel": "912345678",
    "email": "joao.silva@email.com",
    "morada": "Rua das Flores 10, Lisboa",
    "consentimento_rgpd": true,
    "data_registo": "2026-04-01T10:00:00Z",
    "loja_id": 1,
    "trotinetes": [
      {
        "id": 3,
        "marca": "Xiaomi",
        "modelo": "Mi Electric Scooter 3",
        "numero_serie": "XM2024ABC123"
      }
    ]
  }
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `403` | `LOJA_MISMATCH` | Cliente pertence a outra loja |
| `404` | `RESOURCE_NOT_FOUND` | ID não existe |

---

### GET /api/v1/clientes/{id}/historico

**Descrição:** Devolve o histórico de ordens de serviço de um cliente.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA, MECANICO

**Query params:**

| Param | Tipo | Descrição |
|---|---|---|
| `page` | int | Página (padrão: 1) |
| `page_size` | int | Resultados por página (padrão: 20) |

**Response `200`:**
```json
{
  "data": [
    {
      "id": 10,
      "trotinete_numero_serie": "XM2024ABC123",
      "descricao": "Diagnóstico geral + substituição de pneu",
      "estado": "FATURADA",
      "data_entrada": "2026-03-15T09:00:00Z",
      "data_conclusao": "2026-03-16T17:00:00Z",
      "valor_final": 45.50
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `403` | `LOJA_MISMATCH` | Cliente pertence a outra loja |
| `404` | `RESOURCE_NOT_FOUND` | Cliente não existe |

---

## 6. Trotinetes

**Service associado:** `services/trotinete_service.py`  
**Router:** `routers/trotinetes.py`  
**Schemas:** `schemas/trotinete.py`  
**Estado geral:** Mockado na Etapa 3 `[pendente de integração com BD]`

### Validações obrigatórias

| Campo | Regra |
|---|---|
| `cliente_id` | Obrigatório; o cliente deve existir |
| `numero_serie` | Obrigatório; único no sistema; validado no mock service por agora |
| `marca` | Obrigatório |
| `modelo` | Obrigatório |

---

### POST /api/v1/trotinetes

**Descrição:** Regista uma nova trotinete e associa-a a um cliente existente.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA

**Request body:**
```json
{
  "cliente_id": 1,
  "marca": "Xiaomi",
  "modelo": "Mi Electric Scooter 3",
  "numero_serie": "XM2024ABC123",
  "ano_compra": 2024,
  "cor": "Preto",
  "observacoes_tecnicas": "Bateria substituída em 2025. Controlador original."
}
```

**Response `201`:**
```json
{
  "data": {
    "id": 3,
    "cliente_id": 1,
    "marca": "Xiaomi",
    "modelo": "Mi Electric Scooter 3",
    "numero_serie": "XM2024ABC123",
    "ano_compra": 2024,
    "cor": "Preto",
    "observacoes_tecnicas": "Bateria substituída em 2025. Controlador original.",
    "data_registo": "2026-04-28T14:00:00Z"
  },
  "message": "Trotinete registada com sucesso."
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `404` | `RESOURCE_NOT_FOUND` | `cliente_id` não existe |
| `403` | `LOJA_MISMATCH` | Cliente pertence a outra loja |
| `409` | `DUPLICATE_ENTRY` | Número de série já registado |
| `422` | — | Campos obrigatórios em falta |

---

### GET /api/v1/trotinetes/{id}

**Descrição:** Devolve os dados completos de uma trotinete, incluindo histórico sumário de ordens.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA, MECANICO

**Response `200`:**
```json
{
  "data": {
    "id": 3,
    "cliente": {
      "id": 1,
      "nome": "João Silva",
      "telemovel": "912345678"
    },
    "marca": "Xiaomi",
    "modelo": "Mi Electric Scooter 3",
    "numero_serie": "XM2024ABC123",
    "ano_compra": 2024,
    "cor": "Preto",
    "observacoes_tecnicas": "Bateria substituída em 2025. Controlador original.",
    "data_registo": "2026-04-28T14:00:00Z",
    "total_ordens": 2
  }
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `403` | `LOJA_MISMATCH` | Trotinete pertence a outra loja |
| `404` | `RESOURCE_NOT_FOUND` | ID não existe |

---

### GET /api/v1/trotinetes

**Descrição:** Lista trotinetes, com filtro opcional por cliente.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA, MECANICO

**Query params:**

| Param | Tipo | Descrição |
|---|---|---|
| `cliente_id` | int | Filtrar por cliente |
| `numero_serie` | string | Pesquisa por número de série (exact match) |
| `page` | int | Página (padrão: 1) |
| `page_size` | int | Resultados por página (padrão: 20) |

**Response `200`:** Lista paginada de trotinetes (mesmo schema de POST response).

---

## 7. Peças

**Service associado:** `services/peca_service.py`  
**Router:** `routers/pecas.py`  
**Schemas:** `schemas/peca.py`  
**Estado geral:** Mockado na Etapa 3 `[pendente de integração com BD]`

### Regra crítica de preços

Cada peça tem **dois preços distintos** com propósitos completamente diferentes:

| Campo | Uso | Visível em fatura? |
|---|---|---|
| `preco_custo` | Valor interno de aquisição/compra; apenas para gestão financeira interna | **Nunca** |
| `preco_venda` | Valor cobrado ao cliente quando a peça é aplicada numa reparação | **Sempre** |

**O `preco_custo` nunca deve ser usado para calcular o valor final da fatura do cliente.** Esta regra é aplicada no `fatura_service.py` e nunca pode ser contornada.

---

### GET /api/v1/pecas

**Descrição:** Lista o catálogo de peças disponíveis.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** Todos

**Query params:**

| Param | Tipo | Descrição |
|---|---|---|
| `query` | string | Pesquisa por nome ou referência |
| `categoria` | string | Filtrar por categoria (ex: `BATERIA`, `PNEU`, `TRAVAO`) |
| `page` | int | Página (padrão: 1) |
| `page_size` | int | Resultados por página (padrão: 20) |

**Response `200`:**
```json
{
  "data": [
    {
      "id": 1,
      "referencia": "PEC-BAT-001",
      "nome": "Bateria 36V 7.5Ah Xiaomi",
      "categoria": "BATERIA",
      "descricao": "Bateria de substituição compatível com modelos Xiaomi M365 e Pro.",
      "unidade": "unidade",
      "preco_venda": 89.90,
      "ativo": true
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

> `preco_custo` **não é devolvido** em respostas públicas da API. É um campo interno.

---

### GET /api/v1/pecas/{id}

**Descrição:** Devolve os detalhes de uma peça pelo ID.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** Todos

**Response `200`:**
```json
{
  "data": {
    "id": 1,
    "referencia": "PEC-BAT-001",
    "nome": "Bateria 36V 7.5Ah Xiaomi",
    "categoria": "BATERIA",
    "descricao": "Bateria de substituição compatível com modelos Xiaomi M365 e Pro.",
    "unidade": "unidade",
    "preco_venda": 89.90,
    "ativo": true
  }
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `404` | `RESOURCE_NOT_FOUND` | ID não existe |

---

### POST /api/v1/pecas

**Descrição:** Cria uma nova peça no catálogo.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA

**Request body:**
```json
{
  "referencia": "PEC-BAT-001",
  "nome": "Bateria 36V 7.5Ah Xiaomi",
  "categoria": "BATERIA",
  "descricao": "Bateria de substituição compatível com modelos Xiaomi M365 e Pro.",
  "unidade": "unidade",
  "preco_custo": 42.00,
  "preco_venda": 89.90
}
```

**Response `201`:**
```json
{
  "data": {
    "id": 1,
    "referencia": "PEC-BAT-001",
    "nome": "Bateria 36V 7.5Ah Xiaomi",
    "categoria": "BATERIA",
    "preco_venda": 89.90,
    "ativo": true
  },
  "message": "Peça criada com sucesso."
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `409` | `DUPLICATE_ENTRY` | Referência já existe |
| `422` | `VALIDATION_ERROR` | `preco_custo` ou `preco_venda` negativos ou em falta |

---

## 8. Stock

**Service associado:** `services/stock_service.py`  
**Router:** `routers/stock.py`  
**Schemas:** `schemas/stock.py`  
**Estado geral:** Mockado na Etapa 3 `[pendente de integração com BD]`

### Conceitos

- O stock é gerido **por loja**: cada loja tem a sua quantidade de cada peça.
- Cada registo de stock tem um `limite_minimo`. Quando `quantidade <= limite_minimo`, o sistema emite um alerta.
- Movimentos de stock (entradas, transferências) geram um registo de auditoria `[pendente de integração com BD]`.

---

### GET /api/v1/stock

**Descrição:** Lista o stock da loja. Para ADMINISTRADOR, aceita `loja_id` como filtro.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** Todos

**Query params:**

| Param | Tipo | Descrição |
|---|---|---|
| `loja_id` | int | Filtrar por loja (ADMINISTRADOR apenas) |
| `alerta` | bool | Se `true`, devolve apenas peças abaixo do limite mínimo |
| `page` | int | Página (padrão: 1) |
| `page_size` | int | Resultados por página (padrão: 20) |

**Response `200`:**
```json
{
  "data": [
    {
      "peca_id": 1,
      "peca_referencia": "PEC-BAT-001",
      "peca_nome": "Bateria 36V 7.5Ah Xiaomi",
      "loja_id": 1,
      "loja_nome": "DLMCare Lisboa",
      "quantidade": 3,
      "limite_minimo": 5,
      "alerta": true
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

> `"alerta": true` indica que `quantidade <= limite_minimo`.

---

### POST /api/v1/stock/entradas

**Descrição:** Regista a entrada de stock (reposição de peças) numa loja.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA  
**Auditoria:** Gera log de auditoria `STOCK_ENTRADA` `[pendente de integração com BD]`

**Request body:**
```json
{
  "loja_id": 1,
  "peca_id": 1,
  "quantidade": 10,
  "observacoes": "Reposição mensal. Fatura fornecedor #F2026-042."
}
```

**Response `201`:**
```json
{
  "data": {
    "peca_id": 1,
    "peca_nome": "Bateria 36V 7.5Ah Xiaomi",
    "loja_id": 1,
    "quantidade_anterior": 3,
    "quantidade_adicionada": 10,
    "quantidade_atual": 13,
    "alerta": false
  },
  "message": "Entrada de stock registada."
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `403` | `LOJA_MISMATCH` | Utilizador sem acesso à loja indicada |
| `404` | `RESOURCE_NOT_FOUND` | `peca_id` ou `loja_id` não existe |
| `422` | `VALIDATION_ERROR` | `quantidade` <= 0 |

---

### POST /api/v1/stock/transferencias

**Descrição:** Transfere stock de uma loja de origem para uma loja de destino.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA  
**Auditoria:** Gera log de auditoria `STOCK_TRANSFERENCIA` `[pendente de integração com BD]`

**Request body:**
```json
{
  "peca_id": 1,
  "loja_origem_id": 1,
  "loja_destino_id": 2,
  "quantidade": 2,
  "observacoes": "Cedência urgente para Porto."
}
```

**Response `201`:**
```json
{
  "data": {
    "peca_id": 1,
    "peca_nome": "Bateria 36V 7.5Ah Xiaomi",
    "loja_origem_id": 1,
    "loja_destino_id": 2,
    "quantidade_transferida": 2,
    "stock_origem_apos": 11,
    "stock_destino_apos": 3
  },
  "message": "Transferência de stock concluída."
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `400` | `INSUFFICIENT_STOCK` | Stock de origem insuficiente |
| `403` | `LOJA_MISMATCH` | GERENTE_LOJA a tentar transferir de outra loja |
| `404` | `RESOURCE_NOT_FOUND` | `peca_id` ou `loja_id` não existe |
| `422` | `VALIDATION_ERROR` | `loja_origem_id == loja_destino_id`, ou `quantidade` <= 0 |

---

## 9. Ordens de Serviço

**Service associado:** `services/ordem_servico_service.py`  
**Router:** `routers/ordens_servico.py`  
**Schemas:** `schemas/ordem_servico.py`  
**Estado geral:** Mockado na Etapa 3 `[pendente de integração com BD]`

### Estados e ciclo de vida

```
PENDENTE
   │
   ▼
EM_DIAGNOSTICO
   │
   ▼
AGUARDA_APROVACAO
   │
   ▼
EM_REPARACAO ◄──────┐
   │                 │
   ▼                 │
AGUARDA_PECAS ───────┘
   │
   ▼
CONCLUIDA
   │
   ▼
FATURADA


CANCELADA ◄── qualquer estado antes de FATURADA
```

### Transições permitidas

| De | Para | Perfis autorizados |
|---|---|---|
| `PENDENTE` | `EM_DIAGNOSTICO` | ADMINISTRADOR, GERENTE_LOJA, MECANICO |
| `PENDENTE` | `CANCELADA` | ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA |
| `EM_DIAGNOSTICO` | `AGUARDA_APROVACAO` | ADMINISTRADOR, GERENTE_LOJA, MECANICO |
| `EM_DIAGNOSTICO` | `CANCELADA` | ADMINISTRADOR, GERENTE_LOJA |
| `AGUARDA_APROVACAO` | `EM_REPARACAO` | ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA |
| `AGUARDA_APROVACAO` | `CANCELADA` | ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA |
| `EM_REPARACAO` | `AGUARDA_PECAS` | ADMINISTRADOR, GERENTE_LOJA, MECANICO |
| `EM_REPARACAO` | `CONCLUIDA` | ADMINISTRADOR, GERENTE_LOJA, MECANICO |
| `EM_REPARACAO` | `CANCELADA` | ADMINISTRADOR, GERENTE_LOJA |
| `AGUARDA_PECAS` | `EM_REPARACAO` | ADMINISTRADOR, GERENTE_LOJA, MECANICO |
| `AGUARDA_PECAS` | `CANCELADA` | ADMINISTRADOR, GERENTE_LOJA |
| `CONCLUIDA` | `FATURADA` | Apenas via `POST /faturas` — não por esta rota |

Qualquer outra transição devolve `409` com `code: INVALID_STATE_TRANSITION`.

### Notas sobre registo de tempos

- Os endpoints de tempo (`/tempos/iniciar`, `/tempos/parar`) servem exclusivamente para **métricas internas** de eficiência.
- O **tempo de mão de obra não é usado** diretamente para calcular o valor final da fatura.
- A fatura usa o `preco_servico` tabelado, não o tempo registado.

---

### POST /api/v1/ordens-servico

**Descrição:** Cria uma nova ordem de serviço. Estado inicial: `PENDENTE`.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA

**Request body:**
```json
{
  "trotinete_id": 3,
  "loja_id": 1,
  "mecanico_id": 3,
  "descricao_problema": "Não arranca. Bateria parece descarregada mesmo após carga.",
  "prioridade": "NORMAL",
  "preco_servico": 25.00
}
```

> `preco_servico` é o valor comercial/tabelado do serviço prestado. Entra diretamente na fatura.

**Response `201`:**
```json
{
  "data": {
    "id": 10,
    "numero": "OS-2026-0010",
    "trotinete_id": 3,
    "cliente_id": 1,
    "loja_id": 1,
    "mecanico_id": 3,
    "estado": "PENDENTE",
    "prioridade": "NORMAL",
    "descricao_problema": "Não arranca. Bateria parece descarregada mesmo após carga.",
    "preco_servico": 25.00,
    "data_entrada": "2026-04-28T09:00:00Z",
    "data_conclusao": null,
    "pecas_aplicadas": [],
    "tempo_total_minutos": null
  },
  "message": "Ordem de serviço criada."
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `404` | `RESOURCE_NOT_FOUND` | `trotinete_id` ou `mecanico_id` não existe |
| `403` | `LOJA_MISMATCH` | Trotinete ou mecânico pertence a outra loja |
| `422` | `VALIDATION_ERROR` | `preco_servico` negativo ou ausente |

---

### GET /api/v1/ordens-servico/{id}

**Descrição:** Devolve os detalhes completos de uma ordem de serviço.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** Todos

**Response `200`:**
```json
{
  "data": {
    "id": 10,
    "numero": "OS-2026-0010",
    "estado": "EM_REPARACAO",
    "prioridade": "NORMAL",
    "loja_id": 1,
    "loja_nome": "DLMCare Lisboa",
    "cliente": {
      "id": 1,
      "nome": "João Silva",
      "telemovel": "912345678"
    },
    "trotinete": {
      "id": 3,
      "marca": "Xiaomi",
      "modelo": "Mi Electric Scooter 3",
      "numero_serie": "XM2024ABC123"
    },
    "mecanico": {
      "id": 3,
      "nome": "Bruno Mecânico"
    },
    "descricao_problema": "Não arranca. Bateria parece descarregada mesmo após carga.",
    "preco_servico": 25.00,
    "pecas_aplicadas": [
      {
        "peca_id": 1,
        "peca_nome": "Bateria 36V 7.5Ah Xiaomi",
        "quantidade": 1,
        "preco_venda_unitario": 89.90,
        "subtotal": 89.90
      }
    ],
    "subtotal_pecas": 89.90,
    "valor_estimado_total": 114.90,
    "tempo_total_minutos": 45,
    "data_entrada": "2026-04-28T09:00:00Z",
    "data_conclusao": null,
    "fatura_id": null
  }
}
```

---

### GET /api/v1/ordens-servico

**Descrição:** Lista ordens de serviço com filtros.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** Todos

**Query params:**

| Param | Tipo | Descrição |
|---|---|---|
| `loja_id` | int | Filtrar por loja (ADMINISTRADOR apenas) |
| `estado` | string | Filtrar por estado (ex: `PENDENTE`, `EM_REPARACAO`) |
| `mecanico_id` | int | Filtrar por mecânico |
| `data_inicio` | date | Filtrar por data de entrada (ISO 8601) |
| `data_fim` | date | Filtrar por data de entrada (ISO 8601) |
| `page` | int | Página (padrão: 1) |
| `page_size` | int | Resultados por página (padrão: 20) |

**Response `200`:** Lista paginada de ordens (schema sumário).

---

### PATCH /api/v1/ordens-servico/{id}/estado

**Descrição:** Avança ou cancela o estado de uma ordem de serviço.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** Dependente da transição (ver tabela de transições)  
**Auditoria:** Gera log `OS_ESTADO_ALTERADO` `[pendente de integração com BD]`

**Request body:**
```json
{
  "novo_estado": "EM_REPARACAO",
  "observacao": "Cliente aprovou orçamento por telefone."
}
```

**Response `200`:**
```json
{
  "data": {
    "id": 10,
    "estado_anterior": "AGUARDA_APROVACAO",
    "estado_atual": "EM_REPARACAO",
    "alterado_por": "Ana Rececionista",
    "data_alteracao": "2026-04-28T11:00:00Z"
  },
  "message": "Estado da ordem atualizado."
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `403` | `PERMISSION_DENIED` | Perfil não pode fazer esta transição |
| `404` | `RESOURCE_NOT_FOUND` | Ordem não existe |
| `409` | `INVALID_STATE_TRANSITION` | Transição não permitida |

---

### POST /api/v1/ordens-servico/{id}/tempos/iniciar

**Descrição:** Inicia o cronómetro de trabalho do mecânico para esta ordem.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, MECANICO  
**Nota:** Apenas para métricas internas. Não afeta o valor da fatura.

**Response `200`:**
```json
{
  "data": {
    "ordem_servico_id": 10,
    "inicio": "2026-04-28T11:00:00Z"
  },
  "message": "Registo de tempo iniciado."
}
```

---

### POST /api/v1/ordens-servico/{id}/tempos/parar

**Descrição:** Para o cronómetro e acumula o tempo decorrido.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, MECANICO

**Response `200`:**
```json
{
  "data": {
    "ordem_servico_id": 10,
    "inicio": "2026-04-28T11:00:00Z",
    "fim": "2026-04-28T11:45:00Z",
    "minutos_esta_sessao": 45,
    "tempo_total_acumulado_minutos": 45
  },
  "message": "Registo de tempo parado."
}
```

---

### POST /api/v1/ordens-servico/{id}/pecas

**Descrição:** Associa uma peça utilizada à ordem de serviço. O `preco_venda_unitario` é registado no momento da aplicação, para consistência histórica.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, MECANICO

**Request body:**
```json
{
  "peca_id": 1,
  "quantidade": 1
}
```

**Response `201`:**
```json
{
  "data": {
    "peca_id": 1,
    "peca_nome": "Bateria 36V 7.5Ah Xiaomi",
    "quantidade": 1,
    "preco_venda_unitario": 89.90,
    "subtotal": 89.90
  },
  "message": "Peça adicionada à ordem de serviço."
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `400` | `INSUFFICIENT_STOCK` | Stock insuficiente na loja `[pendente de integração com BD]` |
| `404` | `RESOURCE_NOT_FOUND` | `peca_id` não existe |
| `409` | `INVALID_STATE_TRANSITION` | OS em estado `CONCLUIDA`, `FATURADA` ou `CANCELADA` |

---

## 10. Faturação

**Service associado:** `services/fatura_service.py`  
**Router:** `routers/faturas.py`  
**Schemas:** `schemas/fatura.py`  
**Estado geral:** Mockado na Etapa 3 `[pendente de integração com BD]`

### Regra de negócio obrigatória

```
valor_final = preco_servico + subtotal_pecas

subtotal_pecas = soma de (quantidade × preco_venda_unitario) por cada peça aplicada
```

- `preco_servico`: valor comercial/tabelado do serviço, definido na criação da OS.
- `preco_venda_unitario`: valor de venda da peça no momento da sua aplicação (registado em `POST /ordens-servico/{id}/pecas`).
- `preco_custo` **nunca entra neste cálculo**.
- O tempo de mão de obra **não entra diretamente** no valor final.

### Restrições obrigatórias

| Regra | Erro |
|---|---|
| Não pode emitir fatura se OS não estiver `CONCLUIDA` | `400` `ORDER_NOT_CONCLUDED` |
| Não pode existir mais do que uma fatura por OS | `409` `ORDER_ALREADY_INVOICED` |
| Ao emitir fatura, o estado da OS transita automaticamente para `FATURADA` | — |

---

### POST /api/v1/faturas

**Descrição:** Emite a fatura para uma ordem de serviço concluída. Transita a OS para `FATURADA`.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA  
**Auditoria:** Gera log `FATURA_EMITIDA` `[pendente de integração com BD]`

**Request body:**
```json
{
  "ordem_servico_id": 10
}
```

**Response `201`:**
```json
{
  "data": {
    "id": 5,
    "numero": "FAT-2026-0005",
    "ordem_servico_id": 10,
    "data_emissao": "2026-04-28T17:00:00Z",
    "estado": "EMITIDA",
    "cliente": {
      "id": 1,
      "nome": "João Silva",
      "nif": "123456789",
      "morada": "Rua das Flores 10, Lisboa"
    },
    "trotinete": {
      "marca": "Xiaomi",
      "modelo": "Mi Electric Scooter 3",
      "numero_serie": "XM2024ABC123"
    },
    "servico": {
      "descricao": "Diagnóstico + substituição de bateria",
      "preco_servico": 25.00
    },
    "pecas_aplicadas": [
      {
        "peca_referencia": "PEC-BAT-001",
        "peca_nome": "Bateria 36V 7.5Ah Xiaomi",
        "quantidade": 1,
        "preco_venda_unitario": 89.90,
        "subtotal": 89.90
      }
    ],
    "subtotal_pecas": 89.90,
    "valor_final": 114.90,
    "loja": {
      "nome": "DLMCare Lisboa",
      "morada": "Av. da Liberdade 100, 1250-096 Lisboa",
      "telefone": "213000001"
    }
  },
  "message": "Fatura emitida com sucesso."
}
```

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `400` | `ORDER_NOT_CONCLUDED` | OS não está em estado `CONCLUIDA` |
| `403` | `LOJA_MISMATCH` | OS pertence a outra loja |
| `404` | `RESOURCE_NOT_FOUND` | `ordem_servico_id` não existe |
| `409` | `ORDER_ALREADY_INVOICED` | Já existe fatura para esta OS |

---

### GET /api/v1/faturas/{id}

**Descrição:** Devolve o detalhe completo de uma fatura.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA

**Response `200`:** Mesmo schema de `POST /api/v1/faturas`.

**Erros possíveis:**

| Código | `code` | Condição |
|---|---|---|
| `403` | `LOJA_MISMATCH` | Fatura pertence a outra loja |
| `404` | `RESOURCE_NOT_FOUND` | ID não existe |

---

### GET /api/v1/faturas

**Descrição:** Lista faturas com filtros.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA, RECECIONISTA

**Query params:**

| Param | Tipo | Descrição |
|---|---|---|
| `ordem_servico_id` | int | Filtrar pela OS associada |
| `loja_id` | int | Filtrar por loja (ADMINISTRADOR apenas) |
| `data_inicio` | date | Filtrar por data de emissão |
| `data_fim` | date | Filtrar por data de emissão |
| `page` | int | Página (padrão: 1) |
| `page_size` | int | Resultados por página (padrão: 20) |

**Response `200`:** Lista paginada de faturas (schema sumário com `id`, `numero`, `valor_final`, `data_emissao`, `estado`, `cliente_nome`, `ordem_servico_id`).

---

## 11. Dashboard

**Service associado:** `services/dashboard_service.py`  
**Router:** `routers/dashboard.py`  
**Schemas:** `schemas/dashboard.py`  
**Estado geral:** Mockado na Etapa 3 com dados estáticos `[pendente de integração com BD]`

---

### GET /api/v1/dashboard

**Descrição:** Devolve métricas agregadas do sistema para a loja do utilizador autenticado (ou globais para ADMINISTRADOR).  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA

**Query params:**

| Param | Tipo | Descrição |
|---|---|---|
| `loja_id` | int | Filtrar por loja (ADMINISTRADOR apenas) |
| `data_inicio` | date | Início do período |
| `data_fim` | date | Fim do período |

**Response `200`:**
```json
{
  "data": {
    "periodo": {
      "inicio": "2026-04-01",
      "fim": "2026-04-28"
    },
    "ordens_por_estado": {
      "PENDENTE": 4,
      "EM_DIAGNOSTICO": 2,
      "AGUARDA_APROVACAO": 1,
      "EM_REPARACAO": 5,
      "AGUARDA_PECAS": 1,
      "CONCLUIDA": 8,
      "FATURADA": 22,
      "CANCELADA": 3
    },
    "ordens_concluidas_por_loja": [
      { "loja_id": 1, "loja_nome": "DLMCare Lisboa", "total": 14 },
      { "loja_id": 2, "loja_nome": "DLMCare Porto", "total": 8 }
    ],
    "tempo_medio_reparacao_minutos": 127,
    "faturacao_total": 3842.50,
    "pecas_abaixo_stock_minimo": [
      {
        "peca_id": 1,
        "peca_nome": "Bateria 36V 7.5Ah Xiaomi",
        "loja_id": 1,
        "quantidade": 3,
        "limite_minimo": 5
      }
    ],
    "eficiencia_por_mecanico": [
      {
        "mecanico_id": 3,
        "nome": "Bruno Mecânico",
        "ordens_concluidas": 12,
        "tempo_medio_minutos": 118
      }
    ]
  }
}
```

---

## 12. Auditoria

**Service associado:** integrado nos services dos outros módulos  
**Router:** `routers/auditoria.py`  
**Schemas:** `schemas/auditoria.py` (apenas para response)  
**Estado geral:** Mockado na Etapa 3 `[pendente de integração com BD]`

### Eventos registados

| Evento | Gerado por |
|---|---|
| `LOGIN_SUCESSO` | `auth_service` |
| `LOGIN_FALHA` | `auth_service` |
| `ACESSO_NEGADO` | dependency `require_roles` |
| `OS_ESTADO_ALTERADO` | `ordem_servico_service` |
| `STOCK_ENTRADA` | `stock_service` |
| `STOCK_TRANSFERENCIA` | `stock_service` |
| `FATURA_EMITIDA` | `fatura_service` |

---

### GET /api/v1/auditoria

**Descrição:** Lista registos de auditoria.  
**Autenticação exigida:** Sim  
**Perfis autorizados:** ADMINISTRADOR, GERENTE_LOJA

**Query params:**

| Param | Tipo | Descrição |
|---|---|---|
| `evento` | string | Filtrar por tipo de evento |
| `utilizador_id` | int | Filtrar por utilizador que gerou o evento |
| `loja_id` | int | Filtrar por loja (ADMINISTRADOR apenas) |
| `data_inicio` | date | Filtrar por data |
| `data_fim` | date | Filtrar por data |
| `page` | int | Página (padrão: 1) |
| `page_size` | int | Resultados por página (padrão: 20) |

**Response `200`:**
```json
{
  "data": [
    {
      "id": 1,
      "evento": "OS_ESTADO_ALTERADO",
      "descricao": "OS #10 alterada de AGUARDA_APROVACAO para EM_REPARACAO",
      "utilizador_id": 2,
      "utilizador_nome": "Ana Rececionista",
      "loja_id": 1,
      "ip_origem": "192.168.1.10",
      "timestamp": "2026-04-28T11:00:00Z",
      "detalhe": {
        "ordem_servico_id": 10,
        "estado_anterior": "AGUARDA_APROVACAO",
        "estado_novo": "EM_REPARACAO"
      }
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

---

## 13. Tabela-resumo final

| Módulo | Endpoints | Perfis autorizados | Service | Estado Etapa 3 | Dependência BD |
|---|---|---|---|---|---|
| **Auth** | POST /auth/login | Público | `auth_service` | Mockado (users em memória) | Tabela `utilizadores` |
| **Auth** | POST /auth/refresh | Público | `auth_service` | Implementado (JWT stateless) | Nenhuma |
| **Auth** | GET /auth/me | Todos | `auth_service` | Implementado | Nenhuma |
| **Clientes** | GET /clientes | Todos | `cliente_service` | Mockado | Tabela `clientes` |
| **Clientes** | POST /clientes | ADM, GER, REC | `cliente_service` | Mockado | Tabela `clientes` |
| **Clientes** | GET /clientes/{id} | Todos | `cliente_service` | Mockado | Tabela `clientes` |
| **Clientes** | GET /clientes/{id}/historico | Todos | `cliente_service` | Mockado | Tabelas `clientes`, `ordens_servico` |
| **Trotinetes** | POST /trotinetes | ADM, GER, REC | `trotinete_service` | Mockado | Tabela `trotinetes` |
| **Trotinetes** | GET /trotinetes/{id} | Todos | `trotinete_service` | Mockado | Tabela `trotinetes` |
| **Trotinetes** | GET /trotinetes | Todos | `trotinete_service` | Mockado | Tabela `trotinetes` |
| **Peças** | GET /pecas | Todos | `peca_service` | Mockado | Tabela `pecas` |
| **Peças** | GET /pecas/{id} | Todos | `peca_service` | Mockado | Tabela `pecas` |
| **Peças** | POST /pecas | ADM, GER | `peca_service` | Mockado | Tabela `pecas` |
| **Stock** | GET /stock | Todos | `stock_service` | Mockado | Tabelas `stock`, `pecas`, `lojas` |
| **Stock** | POST /stock/entradas | ADM, GER | `stock_service` | Mockado | Tabela `stock` |
| **Stock** | POST /stock/transferencias | ADM, GER | `stock_service` | Mockado | Tabela `stock` |
| **Ordens** | POST /ordens-servico | ADM, GER, REC | `ordem_servico_service` | Mockado | Tabelas `ordens_servico`, `trotinetes`, `utilizadores` |
| **Ordens** | GET /ordens-servico/{id} | Todos | `ordem_servico_service` | Mockado | Tabelas `ordens_servico`, `pecas_os` |
| **Ordens** | GET /ordens-servico | Todos | `ordem_servico_service` | Mockado | Tabela `ordens_servico` |
| **Ordens** | PATCH /ordens-servico/{id}/estado | Depende da transição | `ordem_servico_service` | Mockado | Tabela `ordens_servico` |
| **Ordens** | POST /ordens-servico/{id}/tempos/iniciar | ADM, GER, MEC | `ordem_servico_service` | Mockado | Tabela `tempos_os` (ou in-memory) |
| **Ordens** | POST /ordens-servico/{id}/tempos/parar | ADM, GER, MEC | `ordem_servico_service` | Mockado | Tabela `tempos_os` (ou in-memory) |
| **Ordens** | POST /ordens-servico/{id}/pecas | ADM, GER, MEC | `ordem_servico_service` | Mockado | Tabelas `pecas_os`, `stock` |
| **Faturas** | POST /faturas | ADM, GER, REC | `fatura_service` | Mockado | Tabelas `faturas`, `ordens_servico` |
| **Faturas** | GET /faturas/{id} | ADM, GER, REC | `fatura_service` | Mockado | Tabela `faturas` |
| **Faturas** | GET /faturas | ADM, GER, REC | `fatura_service` | Mockado | Tabela `faturas` |
| **Dashboard** | GET /dashboard | ADM, GER | `dashboard_service` | Mockado (dados estáticos) | Múltiplas tabelas |
| **Auditoria** | GET /auditoria | ADM, GER | *(integrado nos services)* | Mockado (lista estática) | Tabela `auditoria` |

**Legenda:** ADM = ADMINISTRADOR, GER = GERENTE_LOJA, REC = RECECIONISTA, MEC = MECANICO

---

## 14. Notas para implementação backend na Etapa 3

### Ordem recomendada de implementação

A sequência abaixo garante que cada módulo tem as suas dependências prontas antes de começar:

```
1. schemas/  (todos os ficheiros Pydantic)
   Razão: routers e services dependem dos schemas. Criar todos antes de qualquer router.

2. auth/ (jwt.py → password.py → dependencies.py)
   Razão: todos os routers precisam das dependencies de autenticação.

3. routers/auth.py + services/auth_service.py
   Razão: validar que o sistema de tokens funciona antes de proteger outros endpoints.

4. routers/clientes.py + services/cliente_service.py
   Razão: o módulo mais simples, sem dependências internas. Ideal para validar o padrão.

5. routers/trotinetes.py + services/trotinete_service.py

6. routers/pecas.py + services/peca_service.py

7. routers/stock.py + services/stock_service.py

8. routers/ordens_servico.py + services/ordem_servico_service.py
   Razão: módulo mais complexo. Depende de trotinetes, clientes, utilizadores, stock.

9. routers/faturas.py + services/fatura_service.py
   Razão: depende das ordens de serviço estarem completas.

10. routers/dashboard.py + services/dashboard_service.py

11. routers/auditoria.py
    Razão: pode ser implementado com uma lista estática em memória; auditoria real vem com BD.

12. main.py — descomentar e registar todos os routers
```

### Services mockados vs. repositories reais

Os services devem ser desenhados desde o início para facilitar a futura integração com a BD, sem alterar os routers:

- Na Etapa 3: o service manipula uma lista Python em memória (dicionários ou objetos Pydantic).
- Quando a BD estiver disponível: o service passa a chamar o repository correspondente.
- Os routers nunca sabem como os dados são persistidos — apenas chamam o service.

Este padrão garante que a integração com a BD é um swap interno no service, sem impacto no contrato da API.

### Testes

Com os services mockados, é possível escrever testes desde o início usando o `TestClient` do FastAPI:

- Testes unitários dos services (lógica pura, sem HTTP).
- Testes de integração dos routers com `TestClient` (sem BD).
- Testes de validação dos schemas Pydantic (campos obrigatórios, formatos).
- Testes das regras de negócio críticas: transições de estado, cálculo da fatura, permissões RBAC.

### Registo dos routers em `main.py`

O único ficheiro existente a alterar é `backend/app/main.py`: descomentar e registar todos os routers com o prefixo `/api/v1` à medida que cada módulo é implementado. Os includes já estão presentes como comentários.

---

## 15. Fora de âmbito

Os seguintes itens **não fazem parte do trabalho deste elemento do grupo** na Etapa 3:

| Item | Responsável |
|---|---|
| Frontend Vue.js | Outro elemento do grupo |
| Modelos SQLAlchemy (ORM) | Outro elemento do grupo |
| Migrations Alembic | Outro elemento do grupo |
| Schema SQL (CREATE TABLE) | Outro elemento do grupo |
| Scripts SQL (init.sql, seed.sql) | Outro elemento do grupo |
| Repositories reais com queries à BD | A implementar após integração com BD |
| Integração com software certificado de faturação | Fora de âmbito do projeto académico |
| Deploy e infraestrutura de produção | Fora de âmbito da Etapa 3 |

> A ausência de modelos ORM e de repositories reais **não bloqueia** a implementação do backend aplicacional. Os services mockados permitem desenvolver, testar e documentar toda a API de forma independente, em paralelo com o trabalho da base de dados.

---

*Documento gerado em 2026-04-28 — DLMCare Backend, Etapa 3*
