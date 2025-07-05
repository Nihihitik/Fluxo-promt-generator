from pydantic import BaseModel, Field
from typing import Optional


class PromptStyleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class PromptStyleCreate(PromptStyleBase):
    pass


class PromptStyleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None


class PromptStyleResponse(PromptStyleBase):
    id: int

    class Config:
        from_attributes = True