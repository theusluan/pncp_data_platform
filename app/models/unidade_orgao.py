from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class UnidadeOrgao(Base):
    __tablename__ = "unidade_orgao"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uf_nome = Column(String(50))
    uf_sigla = Column(String(2))
    codigo_unidade = Column(String(30))
    municipio_nome = Column(String(100))
    nome_unidade = Column(String(200))
    codigo_ibge = Column(String(10))

    # relacionamento com compras
    compras = relationship("Compra", back_populates="unidade_orgao")
