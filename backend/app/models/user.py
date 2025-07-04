from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, CheckConstraint
from sqlalchemy.orm import DeclarativeBase

Base = DeclarativeBase()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    email_verification = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('length(username) >= 3', name='username_min_length'),
        CheckConstraint("email ~ '^[^@]+@[^@]+\.[^@]+$'", name='email_format'),
    )