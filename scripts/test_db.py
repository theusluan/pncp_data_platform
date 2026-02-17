import os
from sqlalchemy import create_engine

os.environ["PGCLIENTENCODING"] = "UTF8"

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/pncp_db",
    client_encoding="utf8"
)

with engine.connect() as conn:
    print("✅ Conexão com o banco OK")


