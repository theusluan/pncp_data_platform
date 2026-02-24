from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db
from app.models.sync import SyncRun

app = FastAPI(title="PNCP Data Platform API")

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except SQLAlchemyError as e:
        return {"status": "error", "message": "database connection failed", "error": str(e)}

@app.post("/init")
def init_sync(resource_key: str, db: Session = Depends(get_db)):
    try:
        sync_run = SyncRun(resource_key=resource_key, status="initialized")
        db.add(sync_run)
        db.commit()
        db.refresh(sync_run)
        return {"status": "ok", "sync_run": {"id": str(sync_run.id), "resource_key": sync_run.resource_key}}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={"status": "error", "message": "failed to init sync", "error": str(e)})

@app.post("/update")
def update_sync(resource_key: str, processed_rows: int = 0, upserted_rows: int = 0, db: Session = Depends(get_db)):
    try:
        sync_run = db.query(SyncRun).filter(SyncRun.resource_key == resource_key).first()
        if not sync_run:
            raise HTTPException(status_code=404, detail="Sync run not found")

        sync_run.status = "updated"
        sync_run.processed_rows = processed_rows
        sync_run.upserted_rows = upserted_rows

        db.commit()
        db.refresh(sync_run)
        return {"status": "ok", "sync_run": {"id": str(sync_run.id), "status": sync_run.status}}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={"status": "error", "message": "failed to update sync", "error": str(e)})

@app.get("/status/{resource_key}")
def status_sync(resource_key: str, db: Session = Depends(get_db)):
    sync_run = db.query(SyncRun).filter(SyncRun.resource_key == resource_key).first()
    if not sync_run:
        raise HTTPException(status_code=404, detail="Sync run not found")
    return {
        "status": "ok",
        "sync_run": {
            "id": str(sync_run.id),
            "resource_key": sync_run.resource_key,
            "last_run_started_at": str(sync_run.last_run_started_at),
            "last_run_finished_at": str(sync_run.last_run_finished_at),
            "last_success_at": str(sync_run.last_success_at),
            "status": sync_run.status,
            "processed_rows": sync_run.processed_rows,
            "upserted_rows": sync_run.upserted_rows,
            "last_error": sync_run.last_error
        }
    }