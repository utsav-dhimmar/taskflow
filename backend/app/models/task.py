from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.models.enums import ProjectPriority, ProjectStatus


class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    project_id: UUID = Field(foreign_key="projects.id", ondelete="CASCADE")
    title: str
    description: str | None = Field(default=None)
    status: ProjectStatus = Field(default=ProjectStatus.TODO)
    priority: ProjectPriority = Field(default=ProjectPriority.MEDIUM)
    assigned_to: UUID | None = Field(
        default=None, foreign_key="users.id", ondelete="SET NULL"
    )
    created_by: UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    due_datetime: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskActivity(SQLModel, table=True):
    __tablename__ = "task_activities"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    task_id: UUID = Field(foreign_key="tasks.id", ondelete="CASCADE")
    action: str
    performed_by: UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    old_value: str | None = Field(default=None)
    new_value: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
