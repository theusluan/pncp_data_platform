import uuid
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base

class SyncRun(Base):
    __tablename__ = "sync_run"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_key = Column(String(100), nullable=False, unique=True)

    last_run_started_at = Column(DateTime(timezone=True))
    last_run_finished_at = Column(DateTime(timezone=True))
    last_success_at = Column(DateTime(timezone=True))

    status = Column(String(30), nullable=False)

    processed_rows = Column(Integer, default=0)
    upserted_rows = Column(Integer, default=0)

    last_error = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SyncRunHistory(Base):
    __tablename__ = "sync_run_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_key = Column(String(100), nullable=False)

    run_started_at = Column(DateTime(timezone=True), nullable=False)
    run_finished_at = Column(DateTime(timezone=True))

    status = Column(String(30), nullable=False)

    processed_rows = Column(Integer, default=0)
    upserted_rows = Column(Integer, default=0)

    error_message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())