from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, SQLModel

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
    refresh_token: str | None = Field(default=None)
    expires_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )
