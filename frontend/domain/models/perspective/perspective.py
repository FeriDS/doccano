from sqlalchemy import Column, Integer, String, JSON
from app.db.base_class import Base

class Perspetiva(Base):
    __tablename__ = "perspetiva"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    campos = Column(JSON, nullable=True)  # Campos definidos dinamicamente
