# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
import time
from app.core.config import settings

# ------------------ Engine (lazy, seguro para Docker) ------------------
engine = None
MAX_RETRIES = 5
RETRY_INTERVAL = 5  # segundos

def get_engine():
    """Cria a engine do SQLAlchemy com retry para Docker"""
    global engine
    if engine is not None:
        return engine

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            engine = create_engine(
                settings.get_database_url,  # pega a URL do config.py
                pool_pre_ping=True,
            )
            # Testa a conexão
            with engine.connect() as conn:
                print("✅ Conexão com o banco estabelecida!")
            break
        except OperationalError:
            print(f"⏳ Tentativa {attempt}/{MAX_RETRIES} falhou. Esperando {RETRY_INTERVAL}s...")
            time.sleep(RETRY_INTERVAL)
    else:
        raise Exception(
            "❌ Não foi possível conectar ao banco após várias tentativas. "
            "Verifique se o Postgres está rodando e se as credenciais estão corretas."
        )
    return engine

# ------------------ Session ------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=get_engine(),
)

# ------------------ Base ORM ------------------
Base = declarative_base()

# ------------------ Dependency FastAPI ------------------
def get_db():
    """Fornece sessão do SQLAlchemy para FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()