import time
from sqlalchemy.orm import Session
from app.clients.pncp_client import PNCPClient
from app.repositories.sync_run_repository import SyncRunRepository


class PNCPEtlService:
    # Serviço que orquestra a ETL do PNCP (buscar, processar e registrar status)

    def __init__(self):
        self.client = PNCPClient()            # Cliente HTTP responsável por chamar a API do PNCP
        self.sync_repo = SyncRunRepository()  # Repositório que controla o status da sincronização no banco

    def run(
        self,
        db: Session,
        data_inicial: str,
        data_final: str,
        codigo_modalidade: int,
    ):
        # Chave única que identifica essa execução de sync no banco
        resource_key = f"pncp_{data_inicial}_{data_final}_{codigo_modalidade}"
        sync = self.sync_repo.get_or_create(db, resource_key)  # Cria ou recupera o controle da execução

        pagina = 1
        total_processados = 0

        try:
            while True:  # Loop principal de paginação da API
                for attempt in range(3):  # Tenta buscar a página até 3 vezes
                    try:
                        payload = self.client.fetch_page(
                            data_inicial=data_inicial,
                            data_final=data_final,
                            codigo_modalidade=codigo_modalidade,
                            pagina=pagina,
                        )
                        break  # Sai do retry se a chamada à API funcionar
                    except Exception:
                        time.sleep(2 ** attempt)  # Backoff exponencial entre as tentativas
                else:
                    # Executado se todas as tentativas falharem
                    raise Exception(f"Falha ao buscar página {pagina}")

                dados = payload.get("data", [])  # Extrai os registros retornados pela API
                if not dados:
                    break  # Encerra o loop quando não há mais dados (fim da paginação)

                # 👉 aqui depois entra o upsert no banco
                total_processados += len(dados)  # Conta quantos registros foram processados

                pagina += 1  # Avança para a próxima página da API

            # Marca no banco que a execução terminou com sucesso
            self.sync_repo.update_success(
                db,
                sync,
                processed_rows=total_processados,
                upserted_rows=total_processados,
            )

        except Exception as e:
            # Marca no banco que a execução falhou e salva o erro
            self.sync_repo.update_error(db, sync, str(e))
            raise  # Relança a exceção para quem chamou saber que falhou