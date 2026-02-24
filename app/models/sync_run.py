from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    func
)
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    func
)

# Importa a Base do projeto
# Base é a classe "pai" de todos os modelos
# É ela que diz ao SQLAlchemy: "isso aqui vira tabela no banco"
from app.core.database import Base


# Define uma classe que representa a tabela "sync_run"
# Cada instância dessa classe representa uma linha da tabela
class SyncRun(Base):

    # Nome da tabela no banco de dados
    __tablename__ = "sync_run"

    # Coluna id
    # Integer -> número inteiro
    # primary_key=True -> identifica cada registro de forma única
    id = Column(Integer, primary_key=True)

    # Coluna resource_key
    # String(100) -> texto com até 100 caracteres
    # nullable=False -> não pode ser nulo (obrigatório)
    # unique=True -> não pode repetir valores na tabela
    resource_key = Column(String(100), nullable=False, unique=True)

    # Data e hora em que a sincronização começou pela última vez
    last_run_started_at = Column(DateTime)

    # Data e hora em que a sincronização terminou pela última vez
    last_run_finished_at = Column(DateTime)

    # Data e hora da última sincronização feita com sucesso
    last_success_at = Column(DateTime)

    # Status atual da sincronização
    # Exemplo: "running", "success", "error"
    status = Column(String(50))

    # Quantidade total de linhas processadas na última execução
    processed_rows = Column(Integer)

    # Quantidade de linhas que foram inseridas ou atualizadas
    upserted_rows = Column(Integer)

    # Guarda a mensagem do último erro, caso tenha falhado
    # Text é usado para textos longos
    last_error = Column(Text)

    # Data e hora de criação do registro
    # server_default=func.now() -> o próprio banco define a data automaticamente
    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    # Data e hora da última atualização do registro
    # server_default -> valor inicial
    # onupdate -> atualiza automaticamente sempre que o registro mudar
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )