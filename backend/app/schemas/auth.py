from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.db.models.enums import Role

Password = Annotated[str, Field(min_length=6, max_length=32)]


class UserCreate(BaseModel):
    email: EmailStr
    password: Password
    full_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: Password


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    id: UUID | None = None


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool
