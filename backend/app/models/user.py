from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.models.enums import Role


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
    )
    email: str = Field(unique=True, index=True)
    password: str
    full_name: str
    role: Role = Field(default=Role.USER)
    is_active: bool = Field(default=True)
    refresh_token: Optional[str] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
