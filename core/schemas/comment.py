from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=300)

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    content: str | None = Field(None, min_length=1, max_length=300)

class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    author_id: int 
    post_id: int
    content: str
    created_at: datetime
    is_edited: bool
    edited_at: datetime