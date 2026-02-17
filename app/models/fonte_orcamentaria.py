from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base
from sqlalchemy.sql import func

class FonteOrcamentaria(Base):
    __tablename__ = "fontes_orcamentarias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(Integer)
    nome = Column(String(100))
    descricao = Column(String(255))
    data_inclusao = Column(DateTime(timezone=True), default=func.now())

    compra_id = Column(UUID(as_uuid=True), ForeignKey("compra.id"))
    compra = relationship("Compra", back_populates="fontes_orcamentarias")
