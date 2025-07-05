from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PromptRequestBase(BaseModel):
    original_prompt: str = Field(..., min_length=1)
    style_id: Optional[int] = None


class PromptRequestCreate(PromptRequestBase):
    pass


class PromptRequestUpdate(BaseModel):
    generated_prompt: Optional[str] = None


class PromptRequestResponse(PromptRequestBase):
    id: int
    user_id: int
    generated_prompt: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True