from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime 


class UserBase(BaseModel):
    username: str = Field(..., min_length=4, max_length=24)
    email: EmailStr = Field(...)
    
class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=4, max_length=24)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=6, max_length=32)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=32)

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    created_at: datetime

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    """Что сервер возвращает при успешном логине"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefreshRequest(BaseModel):
    refresh_token: str