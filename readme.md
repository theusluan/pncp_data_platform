# PNCP Data Platform

Plataforma de dados para ingestão, controle e monitoramento de informações do
**Portal Nacional de Contratações Públicas (PNCP)**.

Este projeto implementa a **Etapa 1 de um pipeline de dados**, com foco em:
infraestrutura, controle de execuções, versionamento de schema e observabilidade,
utilizando API REST e ambiente totalmente dockerizado.

---

## 🎯 Objetivo do projeto

O objetivo da PNCP Data Platform é criar uma base sólida para:

* Ingestão estruturada de dados do PNCP
* Controle de sincronizações e reprocessamentos
* Registro histórico de execuções (sucesso, erro, tempo)
* Exposição de endpoints para orquestração e monitoramento
* Preparação do ambiente para embeddings e busca vetorial

Nesta **Etapa 1**, não há foco em analytics ou IA, mas sim em **fundação técnica confiável**.

---

## 🧱 Arquitetura (Etapa 1)

### Stack principal

* **API**: FastAPI
* **Servidor ASGI**: Uvicorngit
* **Banco de dados**: PostgreSQL
* **Busca vetorial**: pgvector (habilitado, ainda não explorado)
* **ORM**: SQLAlchemy (2.x)
* **Migrations**: Alembic
* **Infraestrutura**: Docker + Docker Compose

### Componentes

* Container da API (`pncp_api`)
* Container do banco (`pncp_postgres`)
* Comunicação via rede interna Docker

---

## 📂 Estrutura do projeto

```
pncp_data_platform/
├── app/
│   ├── api.py              # Entrypoint da FastAPI
│   ├── core/               # Configurações, banco, sessão
│   ├── models/             # Models ORM (SQLAlchemy)
│   └── services/           # Regras de negócio / ETL
│
├── alembic/                # Migrations
│   ├── versions/
│   └── env.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🗄️ Banco de dados

### Tabelas principais

* `alembic_version` — controle de migrations (esperado)
* `sync_run` — estado atual de cada recurso sincronizado
* `sync_run_history` — histórico completo de execuções
* Tabelas de domínio (PNCP):

  * `compra`
  * `orgao_entidade`
  * `unidade_orgao`
  * `fonte_orcamentaria`

---

## 🌐 Endpoints disponíveis

| Método | Endpoint                 | Descrição                                     |
| ------ | ------------------------ | --------------------------------------------- |
| GET    | `/health`                | Verifica status da API e conexão com o banco  |
| POST   | `/init`                  | Inicializa registros de controle (`sync_run`) |
| POST   | `/update`                | Executa atualização/simulação de carga        |
| GET    | `/status/{resource_key}` | Consulta última execução de um recurso        |

### Documentação automática

* Swagger UI: `http://localhost:8000/docs`

---

## ⚙️ Como rodar o projeto

### Pré-requisitos

* Docker
* Docker Compose

---

### 🐳 Execução via Docker (recomendado)

1. Clone o repositório:

```bash
git clone https://github.com/theusluan/pncp_data_platform.git
cd pncp_data_platform
```

2. Crie o arquivo de ambiente:

```bash
cp .env.example .env
```

3. Suba os containers:

```bash
docker-compose up --build
```

4. Acesse:

* API: `http://localhost:8000`
* Health check: `http://localhost:8000/health`
* Swagger: `http://localhost:8000/docs`

---

## 🧪 Migrations (Alembic)

As migrations são executadas dentro do container da API.

### Executar migrations manualmente

```bash
docker exec -it pncp_api alembic upgrade head
```

A presença da tabela `alembic_version` no banco **é esperada e correta**.

---

## 🧠 Variáveis de ambiente


Arquivo de exemplo (`.env.example`):

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=pncp_db

DATABASE_URL=postgresql+psycopg2://postgres:postgres123@pncp_postgres:5432/pncp_db
```


## 🧪 Como testar os endpoints

Utilize:

* Swagger (`/docs`)
* Postman / Insomnia
* Curl

Exemplo:

```bash
curl http://localhost:8000/health
```

Resposta esperada:

```json
{
  "status": "ok",
  "database": "connected"
}
```

