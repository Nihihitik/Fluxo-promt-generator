from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class EmailVerificationCodeBase(BaseModel):
    """Базовая схема для кода подтверждения email"""
    code: str = Field(..., min_length=6, max_length=6, description="6-значный код подтверждения")


class EmailVerificationCodeCreate(EmailVerificationCodeBase):
    """Схема для создания кода подтверждения email"""
    user_id: int = Field(..., description="ID пользователя")
    expires_at: datetime = Field(..., description="Время истечения кода")


class EmailVerificationCodeUpdate(BaseModel):
    """Схема для обновления кода подтверждения email"""
    is_used: Optional[bool] = Field(None, description="Флаг использования кода")


class EmailVerificationCodeResponse(EmailVerificationCodeBase):
    """Схема ответа с кодом подтверждения email"""
    id: int = Field(..., description="ID кода подтверждения")
    user_id: int = Field(..., description="ID пользователя")
    expires_at: datetime = Field(..., description="Время истечения кода")
    is_used: bool = Field(..., description="Флаг использования кода")
    created_at: datetime = Field(..., description="Время создания кода")

    class Config:
        from_attributes = True


class EmailVerificationRequest(BaseModel):
    """Схема запроса подтверждения email"""
    email: str = Field(..., description="Email пользователя")
    code: str = Field(..., min_length=6, max_length=6, description="6-значный код подтверждения")


class EmailVerificationResponse(BaseModel):
    """Схема ответа подтверждения email"""
    message: str = Field(..., description="Сообщение о результате")
    email_confirmed: bool = Field(False, description="Флаг подтверждения email")


class ResendVerificationRequest(BaseModel):
    """Схема запроса повторной отправки кода"""
    email: str = Field(..., description="Email пользователя")


class ResendVerificationResponse(BaseModel):
    """Схема ответа повторной отправки кода"""
    message: str = Field(..., description="Сообщение о результате отправки")