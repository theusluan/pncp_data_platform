# 🚀 PNCP Data Platform

Plataforma de dados para ingestão, processamento e organização de informações do
**Portal Nacional de Contratações Públicas (PNCP)**.

Este projeto evolui de um pipeline ETL tradicional para uma **Data Platform moderna**, com foco em:

* Ingestão confiável de dados públicos
* Modelagem relacional consistente
* Controle de execuções (idempotência)
* Preparação para busca semântica (embeddings + vetores)

---

# 🎯 Objetivo

Construir uma base sólida para:

✔ Ingestão estruturada de dados do PNCP
✔ Processamento ETL relacional completo
✔ Garantia de integridade entre tabelas
✔ Controle de execuções e reprocessamento
✔ Evolução para busca inteligente (IA / embeddings)

---

# 🧱 Arquitetura

## Stack principal

* **API**: FastAPI
* **Servidor**: Uvicorn
* **Banco**: PostgreSQL
* **ORM**: SQLAlchemy 2.x
* **Migrations**: Alembic
* **Infraestrutura**: Docker + Docker Compose
* **Vetores (futuro)**: pgvector

---

## Componentes

* `pncp_api` → API + ETL
* `pncp_postgres` → Banco de dados
* Comunicação via rede Docker

---

# ⚙️ Pipeline ETL (Atual)

O pipeline implementado realiza:

1. Criação de controle de execução (sync_run)
2. Paginação automática na API do PNCP
3. Retry por página (resiliência)
4. Processamento ETL
5. Inserção relacional:

   * unidade_orgao
   * orgao_entidade
   * compra
   * fontes_orcamentarias
6. Atualização de status final

---

# 🗄️ Modelagem de Dados

## Tabelas principais

### 🔹 Controle

* `sync_run` → execução atual
* `sync_run_history` → histórico completo

---

### 🔹 Domínio (PNCP)

* `compra`
* `orgao_entidade`
* `unidade_orgao`
* `fontes_orcamentarias`
* `amparo_legal`

---

## 🔗 Relacionamentos

unidade_orgao → compra → fontes_orcamentarias
orgao_entidade → compra

✔ Integridade referencial garantida
✔ Foreign Keys funcionando
✔ Pipeline relacional validado

---

# 🔑 Identificação dos dados

O sistema utiliza:

* **UUID (Primary Key)** → interno (seguro e escalável)
* **Campos de negócio** → leitura humana

Exemplo:

UUID → controle interno
numero_compra → identificação real
codigo_unidade → identificação organizacional

---

# 🌐 Endpoints

| Método | Endpoint                 | Descrição                        |
| ------ | ------------------------ | -------------------------------- |
| GET    | `/health`                | Status da API e banco            |
| POST   | `/init`                  | Executa ETL completo             |
| POST   | `/update`                | Atualização incremental (futuro) |
| GET    | `/status/{resource_key}` | Status da execução               |

---

## 📌 Exemplo de execução

POST /init

```json
{
  "dataInicial": "20260128",
  "dataFinal": "20260129",
  "codigoModalidade": 8,
  "resource_key": "insert_relacional_20260128_20260129_mod8"
}
```

---

## ✅ Resposta esperada

```json
{
  "status": "ok",
  "resource_key": "...",
  "total_inseridos": 2643
}
```

---

# 🐳 Como rodar o projeto

## 1. Clonar repositório

```bash
git clone https://github.com/theusluan/pncp_data_platform.git
cd pncp_data_platform
```

---

## 2. Criar `.env`

```bash
cp .env.example .env
```

---

## 3. Subir containers

```bash
docker-compose up --build
```

---

## 4. Acessos

* API → http://localhost:8000
* Swagger → http://localhost:8000/docs
* Health → http://localhost:8000/health

---

# 🧪 Migrations

Rodar dentro do container:

```bash
docker exec -it pncp_api alembic upgrade head
```

---

# 🔍 Validação de dados

```sql
SELECT COUNT(*) FROM compra;
```

```sql
SELECT 
    c.numero_compra,
    u.nome_unidade
FROM compra c
JOIN unidade_orgao u ON u.id = c.unidade_orgao_id
LIMIT 10;
```

---

# 🧠 Próximos passos (Roadmap)

## 🔥 Fase atual (concluída)

* ✔ ETL relacional
* ✔ Controle de execução
* ✔ Migrations
* ✔ Docker

---

## 🚀 Próxima fase

* 🔹 UPSERT (evitar duplicidade)
* 🔹 Carga incremental
* 🔹 Auditoria completa

---

## 🤖 Fase futura (IA)

* 🔹 Embeddings (vectorização)
* 🔹 pgvector
* 🔹 Busca semântica
* 🔹 RAG (chat com dados do PNCP)

---

# 🧠 Conceitos aplicados

* Data Engineering
* ETL Pipeline
* Idempotência
* Modelagem relacional
* Observabilidade
* Arquitetura de dados moderna

---

# 📌 Autor

Desenvolvido por Matheus Luan 🚀
