from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class Compra(Base):
    __tablename__ = "compra"

    # Constraint para evitar duplicação de compras
    __table_args__ = (
        UniqueConstraint("numero_compra", "ano_compra", name="uq_compra_numero_ano"),
    )

    # Campos principais
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_compra = Column(String(50), nullable=False)
    processo = Column(String(50))
    objeto_compra = Column(Text)
    ano_compra = Column(Integer)
    valor_total_homologado = Column(Float)
    modalidade_id = Column(Integer)
    modalidade_nome = Column(String(100))
    situacao_compra_id = Column(Integer)
    situacao_compra_nome = Column(String(100))
    usuario_nome = Column(String(100))
    data_atualizacao = Column(DateTime(timezone=True), default=func.now())
    vector = Column(Vector(1536))

    # Relacionamentos
    orgao_entidade_id = Column(UUID(as_uuid=True), ForeignKey("orgao_entidade.id"))
    unidade_orgao_id = Column(UUID(as_uuid=True), ForeignKey("unidade_orgao.id"))
    amparo_legal_id = Column(UUID(as_uuid=True), ForeignKey("amparo_legal.id"))

    orgao_entidade = relationship("OrgaoEntidade", back_populates="compras")
    unidade_orgao = relationship("UnidadeOrgao", back_populates="compras")
    amparo_legal = relationship("AmparoLegal", back_populates="compras")

    fontes_orcamentarias = relationship(
        "FonteOrcamentaria",
        back_populates="compra",
        cascade="all, delete-orphan"
    )