
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.sync import SyncRun, SyncRunHistory


class SyncService:
    """
    Serviço responsável por controlar o ciclo de vida de uma sincronização:
    - iniciar execução
    - finalizar execução
    - consultar status atual
    """

    def __init__(self, db: Session):
        # Sessão do banco de dados (SQLAlchemy)
        self.db = db

    def start_run(self, resource_key: str) -> SyncRun:
        """
        Inicia (ou reinicia) a sincronização de um recurso.
        Cria o registro se não existir ou reseta se já existir.
        """
        # Data/hora atual em UTC
        now = datetime.now(timezone.utc)

        # Busca no banco se já existe uma sync para esse recurso
        sync_run = (
            self.db.query(SyncRun)
            .filter(SyncRun.resource_key == resource_key)
            .one_or_none()
        )

        if not sync_run:
            # Caso nunca tenha rodado, cria um novo registro
            sync_run = SyncRun(
                resource_key=resource_key,
                status="RUNNING",
                last_run_started_at=now,
                processed_rows=0,
                upserted_rows=0,
            )
            self.db.add(sync_run)
        else:
            # Caso já exista, apenas reinicia os dados da execução
            sync_run.status = "RUNNING"
            sync_run.last_run_started_at = now
            sync_run.last_error = None
            sync_run.processed_rows = 0
            sync_run.upserted_rows = 0

        # Salva alterações no banco
        self.db.commit()

        # Atualiza o objeto com os dados persistidos
        self.db.refresh(sync_run)

        # Retorna o estado atual da sincronização
        return sync_run

    def finish_run(
        self,
        resource_key: str,
        *,
        success: bool,
        processed_rows: int = 0,
        upserted_rows: int = 0,
        error_message: str | None = None,
    ) -> None:
        """
        Finaliza a execução da sincronização e registra o histórico.
        """
        # Data/hora atual em UTC
        now = datetime.now(timezone.utc)

        # Busca a execução atual pelo resource_key
        sync_run = (
            self.db.query(SyncRun)
            .filter(SyncRun.resource_key == resource_key)
            .one()
        )

        # Define o status final com base no sucesso ou erro
        status = "SUCCESS" if success else "ERROR"

        # Atualiza os dados da execução atual
        sync_run.status = status
        sync_run.last_run_finished_at = now
        sync_run.processed_rows = processed_rows
        sync_run.upserted_rows = upserted_rows

        if success:
            # Se deu certo, registra o último sucesso
            sync_run.last_success_at = now
            sync_run.last_error = None
        else:
            # Se deu erro, salva a mensagem do erro
            sync_run.last_error = error_message

        # Cria um registro de histórico da execução
        history = SyncRunHistory(
            resource_key=resource_key,
            run_started_at=sync_run.last_run_started_at,
            run_finished_at=now,
            status=status,
            processed_rows=processed_rows,
            upserted_rows=upserted_rows,
            error_message=error_message,
        )

        # Salva o histórico no banco
        self.db.add(history)
        self.db.commit()

    def get_status(self, resource_key: str) -> SyncRun | None:
        """
        Retorna o status atual da sincronização de um recurso.
        """
        return (
            self.db.query(SyncRun)
            .filter(SyncRun.resource_key == resource_key)
            .one_or_none()
        )