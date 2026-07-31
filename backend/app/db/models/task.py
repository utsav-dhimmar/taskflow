from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

from .enums import ProjectPriority, ProjectStatus


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, index=True, default=uuid4
    )
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, native_enum=False),
        default=ProjectStatus.TODO,
        nullable=False,
    )
    priority: Mapped[ProjectPriority] = mapped_column(
        Enum(ProjectPriority, native_enum=False),
        default=ProjectPriority.MEDIUM,
        nullable=False,
    )
    assigned_to: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, default=None
    )
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    due_datetime: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(UTC),
    )


class TaskActivity(Base):
    __tablename__ = "task_activities"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, index=True, default=uuid4
    )
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[str] = mapped_column(String, nullable=False)
    performed_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    old_value: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )
    new_value: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
