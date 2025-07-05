from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, func, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    is_email_confirmed = Column(Boolean, default=False, nullable=False)
    daily_limit = Column(Integer, default=3, nullable=False)
    requests_today = Column(Integer, default=0, nullable=False)
    last_request_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Связи
    prompt_requests = relationship("PromptRequest", back_populates="user")

    __table_args__ = (
        CheckConstraint(r"email ~ '^[^@]+@[^@]+\.[^@]+$'", name='email_format'),
    )
