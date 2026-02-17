from sqlalchemy import Column, String, CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class OrgaoEntidade(Base):
    __tablename__ = "orgao_entidade"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cnpj = Column(CHAR(14), nullable=False, unique=True)
    razao_social = Column(String(200), nullable=False)
    poder_id = Column(String(10))
    esfera_id = Column(String(10))

    # relacionamento com compras
    compras = relationship("Compra", back_populates="orgao_entidade")
