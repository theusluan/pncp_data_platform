# scripts/test_imports.py

from app.core.database import Base
from app.models.compra import Compra
from app.models.orgao_entidade import OrgaoEntidade
from app.models.unidade_orgao import UnidadeOrgao
from app.models.fonte_orcamentaria import FonteOrcamentaria

print("✅ Todos os imports funcionaram corretamente!")
