from fastapi import APIRouter, Depends          # Ferramentas do FastAPI para criar rotas e injetar dependências
from sqlalchemy.orm import Session              # Tipo da sessão do banco
from app.core.database import get_db             # Função que fornece uma sessão de banco por request
from app.services.pncp_etl_service import PNCPEtlService  # Serviço que executa a ETL do PNCP

router = APIRouter(prefix="/etl/pncp", tags=["ETL PNCP"])
# Cria um grupo de rotas com prefixo e tag para documentação (Swagger)


@router.post("/run")
def run_etl(
    data_inicial: str,
    data_final: str,
    codigo_modalidade: int,
    db: Session = Depends(get_db),
):
    # Endpoint HTTP que dispara manualmente a execução da ETL

    service = PNCPEtlService()  # Instancia o serviço responsável pela lógica da ETL
    service.run(
        db=db,
        data_inicial=data_inicial,
        data_final=data_final,
        codigo_modalidade=codigo_modalidade,
    )  # Executa toda a pipeline de sincronização

    return {"status": "ok"}  # Retorna uma resposta simples indicando que a chamada foi aceita