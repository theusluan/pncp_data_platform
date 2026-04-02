from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import text
from pydantic import BaseModel, Field
from typing import Optional
import requests
import time
from loguru import logger

from app.core.database import get_db
from app.models.sync import SyncRun

# service responsável pelo processamento ETL
from app.services.pncp_etl_service import PNCPEtlService


app = FastAPI(
    title="PNCP Data Platform API",
    description="API responsável por consumir dados públicos do PNCP, armazenar no PostgreSQL e controlar sincronizações.",
    version="1.0.0",
)

PNCP_API_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

MAX_RETRIES_PER_PAGE = 3
RETRY_WAIT_SECONDS = 5
PAGE_SIZE = 10

# 🛑 limite de TESTE (por licitação completa)
MAX_ITENS = 10


# ==========================================================
# ====================== SCHEMAS ===========================
# ==========================================================

class InitRequest(BaseModel):
    dataInicial: str = Field(..., example="20240101")
    dataFinal: str = Field(..., example="20240131")
    codigoModalidade: int = Field(..., example=1)
    resource_key: Optional[str] = Field(default="pncp_init", example="pncp_jan_2024")


class UpdateRequest(BaseModel):
    resource_key: str = Field(..., example="pncp_jan_2024")
    processed_rows: int = Field(default=0, example=120)
    upserted_rows: int = Field(default=0, example=120)


class SyncStatusResponse(BaseModel):
    id: str
    resource_key: str
    last_run_started_at: Optional[str]
    last_run_finished_at: Optional[str]
    last_success_at: Optional[str]
    status: str
    processed_rows: int
    upserted_rows: int
    last_error: Optional[str]

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5


# ==========================================================
# ====================== HEALTHCHECK =======================
# ==========================================================

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except SQLAlchemyError as e:
        return {
            "status": "error",
            "message": "database connection failed",
            "error": str(e),
        }


# ==========================================================
# ========================= INIT ===========================
# ==========================================================

@app.post("/init")
def init_sync(payload: InitRequest, db: Session = Depends(get_db)):

    resource_key = payload.resource_key

    try:
        sync_run = SyncRun(resource_key=resource_key, status="running")
        db.add(sync_run)
        db.commit()
        db.refresh(sync_run)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao iniciar sincronização: {str(e)}",
        )

    service = PNCPEtlService(db)

    pagina = 1
    total_inseridos = 0

    while True:
        success = False

        for tentativa in range(1, MAX_RETRIES_PER_PAGE + 1):
            try:

                response = requests.get(
                    PNCP_API_URL,
                    params={
                        "dataInicial": payload.dataInicial,
                        "dataFinal": payload.dataFinal,
                        "codigoModalidadeContratacao": payload.codigoModalidade,
                        "pagina": pagina,
                        "tamanhoPagina": PAGE_SIZE,
                    },
                    timeout=15,
                )

                response.raise_for_status()

                data = response.json().get("data", [])

                if not data:
                    success = True
                    break

                inseridos_pagina = 0
                limite_atingido = False  # 👈 controle forte

                for item in data:

                    # 🛑 trava ANTES de processar
                    if total_inseridos >= MAX_ITENS:
                        logger.info("🚫 Limite atingido antes de processar")
                        limite_atingido = True
                        break

                    inserted = service.process_item(item)

                    if inserted:
                        total_inseridos += 1
                        inseridos_pagina += 1

                        # 🛑 trava IMEDIATA após inserir
                        if total_inseridos >= MAX_ITENS:
                            logger.info("🚫 Limite atingido após inserir")
                            limite_atingido = True
                            break

                # commit apenas do que foi processado corretamente
                db.commit()

                logger.info(f"Página {pagina} processada ({inseridos_pagina} licitações)")

                if limite_atingido:
                    success = True
                    break

                success = True
                break

            except (requests.RequestException, SQLAlchemyError, IntegrityError) as e:

                db.rollback()
                logger.warning(f"Erro página {pagina}, tentativa {tentativa}: {e}")
                time.sleep(RETRY_WAIT_SECONDS * tentativa)

        if not success:
            logger.error(f"Falha definitiva na página {pagina}")
            break

        # 🛑 parada global
        if total_inseridos >= MAX_ITENS:
            logger.info("🏁 Encerrando por limite de teste")
            break

        pagina += 1

    try:
        sync_run.status = "completed"
        sync_run.processed_rows = total_inseridos
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Erro ao atualizar status final: {e}")

    return {
        "status": "ok",
        "resource_key": resource_key,
        "total_inseridos": total_inseridos,
        "limite": MAX_ITENS,
    }


# ==========================================================
# ======================== UPDATE ==========================
# ==========================================================

@app.post("/update")
def update_sync(payload: UpdateRequest, db: Session = Depends(get_db)):

    sync_run = db.query(SyncRun).filter(SyncRun.resource_key == payload.resource_key).first()

    if not sync_run:
        raise HTTPException(status_code=404, detail="Sync run não encontrada")

    try:
        sync_run.status = "updated"
        sync_run.processed_rows = payload.processed_rows
        sync_run.upserted_rows = payload.upserted_rows

        db.commit()
        db.refresh(sync_run)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok", "resource_key": payload.resource_key}


# ==========================================================
# ========================= STATUS =========================
# ==========================================================

@app.get("/status/{resource_key}", response_model=SyncStatusResponse)
def status_sync(resource_key: str, db: Session = Depends(get_db)):

    sync_run = db.query(SyncRun).filter(SyncRun.resource_key == resource_key).first()

    if not sync_run:
        raise HTTPException(status_code=404, detail="Sync run não encontrada")

    return SyncStatusResponse(
        id=str(sync_run.id),
        resource_key=sync_run.resource_key,
        last_run_started_at=str(sync_run.last_run_started_at),
        last_run_finished_at=str(sync_run.last_run_finished_at),
        last_success_at=str(sync_run.last_success_at),
        status=sync_run.status,
        processed_rows=sync_run.processed_rows,
        upserted_rows=sync_run.upserted_rows,
        last_error=sync_run.last_error,
    )

# ==========================================================
# ==================== SEARCH (NOVO) =======================
# ==========================================================

@app.post("/search")
def search(payload: SearchRequest, db: Session = Depends(get_db)):
    """
    Endpoint de busca semântica

    Recebe um texto e retorna compras similares
    """

    service = PNCPEtlService(db)

    try:
        results = service.search_similar(
            query=payload.query,
            limit=payload.limit
        )

        return {
            "query": payload.query,
            "results": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )