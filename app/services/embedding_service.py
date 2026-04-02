# app/services/embedding_service.py

import random
import hashlib
from typing import List, Optional


def generate_embedding(text: Optional[str]) -> Optional[List[float]]:
    """
    Gera um embedding FAKE (mock) para testes.

    🔹 IMPORTANTE:
    - Não usamos OpenAI ainda (sem custo)
    - Criamos um vetor determinístico (mesmo texto = mesmo vetor)
    - Isso permite testar busca por similaridade

    🔹 Como funciona:
    - Transformamos o texto em um "seed" (número base)
    - Usamos esse seed para gerar números aleatórios consistentes
    - Resultado: vetor de 1536 dimensões (igual OpenAI)

    🔹 Futuro:
    - Aqui será substituído por chamada real de IA
    """

    # Se não tiver texto, não gera embedding
    if not text:
        return None

    # 🔥 Converte texto em número fixo (hash)
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16)

    # 🔥 Garante que o "aleatório" seja sempre igual para o mesmo texto
    random.seed(seed)

    # 🔥 Gera vetor com 1536 dimensões
    return [random.random() for _ in range(1536)]