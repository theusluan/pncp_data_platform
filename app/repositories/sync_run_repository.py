from sqlalchemy.orm import Session  # Tipo da sessão usada para conversar com o banco
from app.models.sync import SyncRun  # Modelo ORM que representa a tabela sync_run
from datetime import datetime        # Usado para registrar datas e horários


class SyncRunRepository:
    # Classe responsável por ler e escrever dados de sincronização no banco

    def get_or_create(self, db: Session, resource_key: str) -> SyncRun:
        # Busca no banco uma sincronização existente pelo identificador do recurso
        sync = (
            db.query(SyncRun)                         # Inicia uma consulta na tabela SyncRun
            .filter(SyncRun.resource_key == resource_key)  # Filtra pelo resource_key informado
            .first()                                  # Retorna o primeiro registro encontrado
        )

        if not sync:
            # Cria um novo registro se ainda não existir no banco
            sync = SyncRun(
                resource_key=resource_key,            # Identifica qual recurso está sendo sincronizado
                status="running",                     # Marca que a sincronização está em execução
                last_run_started_at=datetime.utcnow(),# Registra quando a sync começou
            )
            db.add(sync)                              # Adiciona o novo objeto à sessão do banco
            db.commit()                               # Salva o novo registro definitivamente no banco
            db.refresh(sync)                          # Atualiza o objeto com dados gerados pelo banco (ex: id)

        return sync                                   # Retorna o registro encontrado ou criado

    def update_success(
        self,
        db: Session,
        sync: SyncRun,
        processed_rows: int,
        upserted_rows: int,
    ):
        # Atualiza o registro para indicar que a sincronização foi concluída com sucesso
        sync.status = "success"                       # Define o status como sucesso
        sync.last_run_finished_at = datetime.utcnow() # Registra quando a sync terminou
        sync.last_success_at = datetime.utcnow()      # Registra a última execução bem-sucedida
        sync.processed_rows = processed_rows          # Salva quantas linhas foram processadas
        sync.upserted_rows = upserted_rows            # Salva quantas linhas foram inseridas/atualizadas
        db.commit()                                   # Grava todas as alterações no banco

    def update_error(self, db: Session, sync: SyncRun, error: str):
        # Atualiza o registro para indicar que a sincronização falhou
        sync.status = "failed"                        # Define o status como erro
        sync.last_run_finished_at = datetime.utcnow() # Registra quando a sync terminou
        sync.last_error = error                       # Salva a mensagem de erro ocorrida
        db.commit()                                   # Grava o estado de erro no banco