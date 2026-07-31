from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

from .enums import Role


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, index=True, unique=True, default=uuid4
    )

    email: Mapped[str] = mapped_column(unique=True, index=True)

    password: Mapped[str] = mapped_column(unique=True)

    full_name: Mapped[str] = mapped_column(String(30))

    role: Mapped[Role] = mapped_column(default=Role.USER)

    is_active: Mapped[bool] = mapped_column(default=True)

    refresh_token: Mapped[str | None] = mapped_column(
        default=None, nullable=True
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
