from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.database import Base
from app.core.config import settings 

# Importar seus models
from app.models.sync import SyncRun, SyncRunHistory
from app.models.compra import Compra
from app.models.orgao_entidade import OrgaoEntidade
from app.models.unidade_orgao import UnidadeOrgao
from app.models.fonte_orcamentaria import FonteOrcamentaria

config = context.config

# ------------------ URL DB ------------------
config.set_main_option(
    "sqlalchemy.url",
    settings.get_database_url  # ⚡ Sem parênteses
)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata para autogenerate
target_metadata = Base.metadata

# ------------------ Offline ------------------
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# ------------------ Online ------------------
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()