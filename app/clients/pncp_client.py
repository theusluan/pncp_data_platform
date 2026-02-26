import requests
from typing import Dict


class PNCPClient:
    BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

    def fetch_page(
        self,
        data_inicial: str,
        data_final: str,
        codigo_modalidade: int,
        pagina: int,
        tamanho_pagina: int = 25,
        timeout: int = 30,
    ) -> Dict:
        params = {
            "dataInicial": data_inicial,
            "dataFinal": data_final,
            "codigoModalidadeContratacao": codigo_modalidade,
            "pagina": pagina,
            "tamanhoPagina": tamanho_pagina,
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=timeout,
        )

        response.raise_for_status()
        return response.json()