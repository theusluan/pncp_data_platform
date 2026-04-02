from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.compra import Compra
from app.models.orgao_entidade import OrgaoEntidade
from app.models.unidade_orgao import UnidadeOrgao
from app.models.amparo_legal import AmparoLegal
from app.models.fonte_orcamentaria import FonteOrcamentaria

from app.services.embedding_service import generate_embedding


class PNCPEtlService:
    """
    Service responsável por:
    - Processar dados da API PNCP (ETL)
    - Inserir dados no banco
    - Gerar embeddings
    - Realizar busca semântica
    """

    def __init__(self, db: Session):
        self.db = db

    # ==================================================
    # =================== ETL ===========================
    # ==================================================

    def process_item(self, item: dict):
        """
        Processa um item da API e insere no banco
        evitando duplicação
        """

        from loguru import logger

        # 🔹 Log simples para debug
        logger.warning("====================================")
        logger.warning(f"NUMERO COMPRA: {item.get('numeroCompra')}")
        logger.warning(f"OBJETO API: {item.get('objetoCompra')}")

        # --------------------------------------------------
        # 1️⃣ DEDUPLICAÇÃO
        # --------------------------------------------------

        compra_existente = self.db.query(Compra).filter(
            Compra.numero_compra == item.get("numeroCompra"),
            Compra.ano_compra == item.get("anoCompra"),
        ).first()

        # Se já existe, não insere novamente
        if compra_existente:
            return False

        # --------------------------------------------------
        # 2️⃣ RELACIONAMENTOS
        # --------------------------------------------------

        orgao = self._get_or_create_orgao(item.get("orgaoEntidade"))
        unidade = self._get_or_create_unidade(item.get("unidadeOrgao"))
        amparo = self._get_or_create_amparo(item.get("amparoLegal"))

        # --------------------------------------------------
        # 3️⃣ EMBEDDING
        # --------------------------------------------------

        objeto = item.get("objetoCompra")

        # 🔥 Gera vetor baseado no texto
        embedding = generate_embedding(objeto)

        if embedding:
            logger.warning(f"Embedding gerado com {len(embedding)} dimensões")
        else:
            logger.warning("Embedding NÃO gerado")

        # --------------------------------------------------
        # 4️⃣ CRIA COMPRA
        # --------------------------------------------------

        compra = Compra(
            numero_compra=item.get("numeroCompra"),
            processo=item.get("processo"),
            objeto_compra=objeto,
            ano_compra=item.get("anoCompra"),
            valor_total_homologado=item.get("valorTotalHomologado"),
            modalidade_id=item.get("modalidadeId"),
            modalidade_nome=item.get("modalidadeNome"),
            situacao_compra_id=item.get("situacaoCompraId"),
            situacao_compra_nome=item.get("situacaoCompraNome"),
            usuario_nome=item.get("usuarioNome"),
            orgao_entidade_id=orgao.id if orgao else None,
            unidade_orgao_id=unidade.id if unidade else None,
            amparo_legal_id=amparo.id if amparo else None,

            # 🔥 NOVO CAMPO (embedding)
            vector=embedding
        )

        self.db.add(compra)

        # 🔥 Garante ID antes de inserir filhos
        self.db.flush()

        # --------------------------------------------------
        # 5️⃣ FONTES ORÇAMENTÁRIAS
        # --------------------------------------------------

        fontes = item.get("fontesOrcamentarias", [])

        for fonte in fontes:
            fonte_obj = FonteOrcamentaria(
                codigo=fonte.get("codigo"),
                nome=fonte.get("nome"),
                descricao=fonte.get("descricao"),
                compra_id=compra.id
            )
            self.db.add(fonte_obj)

        return True

    # ==================================================
    # ============ BUSCA SEMÂNTICA (NOVO) ===============
    # ==================================================

    def search_similar(self, query: str, limit: int = 5):
        """
        Busca compras similares com base no embedding

        🔹 Como funciona:
        1. Gera embedding da query
        2. Compara com embeddings do banco
        3. Retorna os mais próximos
        """

        from loguru import logger

        # 🔥 Gera embedding da busca
        embedding = generate_embedding(query)

        if not embedding:
            return []

        logger.warning(f"Buscando similares para: {query}")

        # 🔥 Query usando pgvector (<-> = distância)
        sql = text("""
            SELECT 
                id,
                objeto_compra,
                vector <-> :embedding AS distancia
            FROM compra
            WHERE vector IS NOT NULL
            ORDER BY vector <-> :embedding
            LIMIT :limit
        """)

        result = self.db.execute(
            sql,
            {
                "embedding": embedding,
                "limit": limit
            }
        )

        # 🔥 Formata resposta
        return [
            {
                "id": str(row.id),
                "objeto_compra": row.objeto_compra,
                "distancia": float(row.distancia)
            }
            for row in result
        ]

    # ==================================================
    # ========= MÉTODOS AUXILIARES ======================
    # ==================================================

    def _get_or_create_orgao(self, data):

        if not data:
            return None

        orgao = self.db.query(OrgaoEntidade).filter(
            OrgaoEntidade.cnpj == data.get("cnpj")
        ).first()

        if orgao:
            return orgao

        orgao = OrgaoEntidade(
            cnpj=data.get("cnpj"),
            razao_social=data.get("razaoSocial"),
            poder_id=data.get("poderId"),
            esfera_id=data.get("esferaId"),
        )

        self.db.add(orgao)
        self.db.flush()

        return orgao

    def _get_or_create_unidade(self, data):

        if not data:
            return None

        unidade = self.db.query(UnidadeOrgao).filter(
            UnidadeOrgao.codigo_unidade == data.get("codigoUnidade")
        ).first()

        if unidade:
            return unidade

        unidade = UnidadeOrgao(
            uf_nome=data.get("ufNome"),
            uf_sigla=data.get("ufSigla"),
            codigo_unidade=data.get("codigoUnidade"),
            municipio_nome=data.get("municipioNome"),
            nome_unidade=data.get("nomeUnidade"),
            codigo_ibge=data.get("codigoIbge"),
        )

        self.db.add(unidade)
        self.db.flush()

        return unidade

    def _get_or_create_amparo(self, data):

        if not data:
            return None

        amparo = self.db.query(AmparoLegal).filter(
            AmparoLegal.codigo == data.get("codigo")
        ).first()

        if amparo:
            return amparo

        amparo = AmparoLegal(
            codigo=data.get("codigo"),
            nome=data.get("nome"),
            descricao=data.get("descricao"),
        )

        self.db.add(amparo)
        self.db.flush()

        return amparo