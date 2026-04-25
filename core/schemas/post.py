
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None

class PostResponse(BaseModel):
    id: int
    title: str
    description: str | None = ""
    author_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)