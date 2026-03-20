from sqlalchemy.orm import Session

from app.models.compra import Compra
from app.models.orgao_entidade import OrgaoEntidade
from app.models.unidade_orgao import UnidadeOrgao
from app.models.amparo_legal import AmparoLegal
from app.models.fonte_orcamentaria import FonteOrcamentaria


class PNCPEtlService:

    def __init__(self, db: Session):
        # recebe sessão do banco para executar operações
        self.db = db


    def process_item(self, item: dict):
        """
        Processa um item retornado da API do PNCP
        aplicando inserção relacional e evitando duplicação.
        """

        # --------------------------------------------------
        # 1️⃣ DEDUPLICAÇÃO DE COMPRA
        # --------------------------------------------------

        compra_existente = self.db.query(Compra).filter(
            Compra.numero_compra == item.get("numeroCompra"),
            Compra.ano_compra == item.get("anoCompra"),
        ).first()

        # se compra já existir não insere novamente
        if compra_existente:
            return False


        # --------------------------------------------------
        # 2️⃣ RELACIONAMENTOS
        # --------------------------------------------------

        # cria ou recupera registros relacionados
        orgao = self._get_or_create_orgao(item.get("orgaoEntidade"))
        unidade = self._get_or_create_unidade(item.get("unidadeOrgao"))
        amparo = self._get_or_create_amparo(item.get("amparoLegal"))


        # --------------------------------------------------
        # 3️⃣ CRIA COMPRA
        # --------------------------------------------------

        compra = Compra(
            numero_compra=item.get("numeroCompra"),
            processo=item.get("processo"),
            objeto_compra=item.get("objeto"),
            ano_compra=item.get("anoCompra"),
            valor_total_homologado=item.get("valorTotalHomologado"),
            modalidade_id=item.get("modalidadeId"),
            modalidade_nome=item.get("modalidadeNome"),
            situacao_compra_id=item.get("situacaoCompraId"),
            situacao_compra_nome=item.get("situacaoCompraNome"),
            usuario_nome=item.get("usuarioNome"),
            orgao_entidade_id=orgao.id if orgao else None,
            unidade_orgao_id=unidade.id if unidade else None,
            amparo_legal_id=amparo.id if amparo else None
        )

        # adiciona compra na sessão
        self.db.add(compra)

        # flush gera ID da compra antes de inserir relacionamentos
        self.db.flush()


        # --------------------------------------------------
        # 4️⃣ FONTES ORÇAMENTÁRIAS
        # --------------------------------------------------

        fontes = item.get("fontesOrcamentarias", [])

        for fonte in fontes:

            # cria fonte orçamentária vinculada à compra
            fonte_obj = FonteOrcamentaria(
                codigo=fonte.get("codigo"),
                nome=fonte.get("nome"),
                descricao=fonte.get("descricao"),
                compra_id=compra.id
            )

            self.db.add(fonte_obj)

        # retorna True indicando que houve inserção
        return True


    def _get_or_create_orgao(self, data):

        # se não houver dados retorna vazio
        if not data:
            return None

        # busca órgão pelo CNPJ
        orgao = self.db.query(OrgaoEntidade).filter(
            OrgaoEntidade.cnpj == data.get("cnpj")
        ).first()

        if orgao:
            return orgao

        # cria novo órgão caso não exista
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

        # busca unidade pelo código
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

        # busca amparo legal pelo código
        amparo = self.db.query(AmparoLegal).filter(
            AmparoLegal.codigo == data.get("codigo")
        ).first()

        if amparo:
            return amparo

        # cria novo amparo legal
        amparo = AmparoLegal(
            codigo=data.get("codigo"),
            nome=data.get("nome"),
            descricao=data.get("descricao"),
        )

        self.db.add(amparo)
        self.db.flush()

        return amparo