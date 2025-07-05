from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional, List


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    daily_limit: Optional[int] = None
    is_email_confirmed: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_email_confirmed: bool
    daily_limit: int
    requests_today: int
    last_request_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class EmailConfirmation(BaseModel):
    email: EmailStr
    code: str