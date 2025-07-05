from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .base import Base


class PromptRequest(Base):
    __tablename__ = "prompt_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_prompt = Column(String, nullable=False)
    style_id = Column(Integer, ForeignKey("prompt_styles.id"), nullable=True)
    generated_prompt = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Связи
    user = relationship("User", back_populates="prompt_requests")
    style = relationship("PromptStyle", back_populates="prompt_requests")