from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class AmparoLegal(Base):
    __tablename__ = "amparo_legal"

    # ----- Campos principais -----
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(Integer, nullable=False)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)

    # ----- Relacionamento com Compra -----
    compras = relationship(
        "Compra",
        back_populates="amparo_legal",
        cascade="all, delete-orphan"
    )