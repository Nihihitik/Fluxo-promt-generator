from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class PromptStyle(Base):
    __tablename__ = "prompt_styles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String, nullable=True)

    # Связи
    prompt_requests = relationship("PromptRequest", back_populates="style")